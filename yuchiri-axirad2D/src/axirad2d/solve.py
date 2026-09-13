# -*- coding: utf-8 -*-
"""[EN] Newton iteration and the run driver.

Specification sections 12, 13, 14.  Serial and MPI results are bit-for-bit
identical: partial results are placed in rank order rather than summed.

[KO] Newton 반복과 실행 드라이버.

See USER_GUIDE sections 9 and 10 (solver, parallel, output).
공개 문서 USER_GUIDE 9·10장 참조.
"""
from __future__ import annotations
import time
import numpy as np
import scipy.sparse.linalg as spla
from .assemble import Assembler, BCError
from .mesh import Mesh
from . import surfaces, montecarlo


class ConvergenceError(Exception):
    pass


def _energy_scale(pin_abs, R, A):
    """[EN] Physical scale for normalising the energy imbalance.

    The natural scale is the heat THROUGHPUT, not the net input.  A problem
    driven only by Dirichlet conditions has zero net input yet a perfectly
    real heat flow through the boundary, so normalising by the net input alone
    divides by zero and reports a converged solution as a failure.

    [KO] 에너지 불균형을 정규화하는 물리적 규모.
    자연스러운 규모는 순 유입이 아니라 '열 처리량' 이다.  Dirichlet 만으로
    구동되는 문제는 순 유입이 0 이지만 경계로 실제 열이 흐르므로, 순 유입으로만
    나누면 0 으로 나누게 되고 수렴한 해를 실패로 보고하게 된다.
    """
    thru = float(np.abs(R[A.dir_nodes]).sum()) if len(A.dir_nodes) else 0.0
    return max(pin_abs, thru, 1e-30)


# ----------------------------------------------------------------------
def gebhart_parallel(S, n_ray, seed, n_bounce_max, leak_tol, mode, rep):
    """직렬 또는 MPI. 결과는 비트 단위로 동일하다 (§13.3).

    소스 세그먼트를 랭크에 나누고, 랭크 순서로 행을 이어 붙인다.
    합산이 아니라 배치이므로 순서 고정이 자명하게 성립한다.
    """
    ns = len(S)
    if mode == "serial":
        B, lo, lb = montecarlo.gebhart(S, n_ray, seed, n_bounce_max, leak_tol,
                                       None, rep)
        rep["parallel_mode"], rep["mpi_size"] = "serial", 1
        return B, lo, lb
    if mode != "mpi":
        raise ValueError("parallel 은 'serial' 또는 'mpi'")
    try:
        from mpi4py import MPI          # noqa
    except Exception as exc:            # §13.2 — 조용히 직렬로 떨어지지 않는다
        raise RuntimeError(
            "parallel='mpi' 를 요청했으나 mpi4py 임포트에 실패했다: %r" % (exc,))
    comm = MPI.COMM_WORLD
    rank, size = comm.Get_rank(), comm.Get_size()
    mine = np.arange(rank, ns, size)
    Bp, lop, lbp = montecarlo.gebhart(S, n_ray, seed, n_bounce_max, leak_tol,
                                      mine, rep)
    B = np.zeros((ns, ns))
    lo = np.zeros(ns, dtype=np.int64)
    lb = np.zeros(ns, dtype=np.int64)
    for r in range(size):                       # 랭크 순서 고정 (§13.3)
        idx = comm.bcast(mine if r == rank else None, root=r)
        Br = comm.bcast(Bp[idx] if r == rank else None, root=r)
        lor = comm.bcast(lop[idx] if r == rank else None, root=r)
        lbr = comm.bcast(lbp[idx] if r == rank else None, root=r)
        B[idx] = Br
        lo[idx] = lor
        lb[idx] = lbr
    rep["parallel_mode"], rep["mpi_size"] = "mpi", size
    montecarlo._diagnose(S, B, lo, lb, n_ray, leak_tol, rep)
    return B, lo, lb


# ----------------------------------------------------------------------
def solve_steady(mesh: Mesh, materials: dict, bcs: list, rad: dict,
                 solver: dict, report: dict, blood: dict | None = None):
    t0 = time.time()
    rep = report

    # --- 격자 검증 (§9) ------------------------------------------------
    mesh.check(bump=solver.get("quad_bump", 0), report=rep)

    # --- 복사면 추출 (§10.2) -------------------------------------------
    S = surfaces.extract(mesh, materials,
                         float(rad.get("boundary_emissivity", 1.0)), rep)

    # --- 환경 복사와의 중첩 검사 (§8.5) ---------------------------------
    seg_keys = {(min(a, b), max(a, b)) for a, b in zip(S.n1, S.n2)}
    for bc in bcs:
        if bc["type"] != "env_radiation":
            continue
        from .assemble import faces_from_nset
        F = faces_from_nset(mesh, bc["nset"])
        clash = []
        for e, le in F.items:
            a, b, _ = mesh.edge_node_ids(e, le)
            if (min(a, b), max(a, b)) in seg_keys:
                clash.append((int(a), int(b)))
        if clash:
            rep["env_radiation_overlap"] = clash
            raise RuntimeError(
                "§8.5 위반 — 환경 복사 집합 '%s' 이 자동 복사면과 %d 개 변에서 "
                "겹친다. 에너지가 이중 계산되므로 중단한다." % (bc["nset"], len(clash)))

    # --- Gebhart 계수 (§10.5 — 실행당 1회) ------------------------------
    B = np.zeros((0, 0))
    rep.setdefault("parallel_mode", str(solver.get("parallel", "serial")))
    rep.setdefault("mpi_size", 1)
    if len(S):
        B, _, _ = gebhart_parallel(
            S, int(rad.get("n_ray", 20000)), int(rad.get("seed", 12345)),
            int(rad.get("n_bounce_max", 20)), float(rad.get("leak_tol", 1e-5)),
            str(solver.get("parallel", "serial")), rep)
    rep["time_radiation_s"] = time.time() - t0

    # --- Newton (§12.2, §12.4) ------------------------------------------
    A = Assembler(mesh, materials, bcs, S if len(S) else None, B,
                  bump=solver.get("quad_bump", 0), blood=blood)
    # 온도 기준점이 하나도 없으면 정상상태 해가 유일하지 않다 (행렬이 특이).
    #   그 경우 Newton 은 발산하고 "수렴하지 않았다" 로 끝나 원인을 가린다.
    #   무엇이 없는지 먼저 말하고 멈춘다.
    # A steady solution needs a temperature reference; without one the matrix is
    # singular and Newton merely diverges, which hides the real cause.
    kinds = {b.get("type") for b in bcs}
    if not (kinds & {"dirichlet", "convection", "env_radiation"}):
        raise BCError(
            "온도 기준점이 될 경계조건이 없다. dirichlet, convection, "
            "env_radiation 중 하나 이상이 필요하다. 이대로는 정상상태 해가 "
            "유일하지 않다 (행렬이 특이). / No boundary condition fixes a "
            "temperature reference; the steady problem is not unique.")

    T = np.full(mesh.nn, float(solver.get("T_init", 300.0)))
    T[A.dir_nodes] = A.dir_vals
    eps_T = float(solver.get("eps_T", 1.0e-6))
    eps_E = float(solver.get("eps_E", 1.0e-8))
    itmax = int(solver.get("max_iter", 50))
    hist, converged = [], False
    for it in range(1, itmax + 1):
        R, J, power = A.residual_jacobian(T)
        # 에너지 불균형은 '열 처리량' 으로 정규화한다.
        #   Dirichlet 만 있고 열원이 없는 문제에서는 sum(power) 가 0 이 되어
        #   0 으로 나누게 된다.  그런 문제에서도 실제로는 Dirichlet 경계를 통해
        #   열이 흐르므로, 반력의 절대합이 물리적인 규모를 준다.
        Pin = abs(power["source"]) + sum(abs(v) for k, v in power.items()
                                         if k not in ("source", "radiation_net"))
        Pscale = _energy_scale(Pin, R, A)
        eimb = abs(float(R[A.free_mask].sum())) / Pscale
        Rd, Jd = A.apply_dirichlet(R, J, T)
        dT = spla.spsolve(Jd.tocsc(), -Rd)
        if not np.all(np.isfinite(dT)):
            raise ConvergenceError("선형 해에 비유한값이 나왔다 (반복 %d)" % it)
        Tspan = max(T.max() - T.min(), 1.0)
        step = float(np.abs(dT).max()) / Tspan
        hist.append(dict(iter=it, step=step, energy_imbalance=eimb,
                         Tmin=float(T.min()), Tmax=float(T.max())))
        T = T + dT
        if step < eps_T and eimb < eps_E:        # AND 조건 (§12.4)
            converged = True
            break
    rep["iterations"] = hist
    rep["converged"] = converged

    R, J, power = A.residual_jacobian(T)
    rep["power"] = power
    rep["reaction_dirichlet"] = float(R[A.dir_nodes].sum())
    Pin = power["source"] + sum(v for k, v in power.items()
                                if k not in ("source", "radiation_net"))
    rep["power_in_total"] = Pin
    scale = _energy_scale(abs(Pin), R, A)
    rep["energy_scale_W"] = scale
    rep["energy_residual_rel"] = abs(Pin + rep["reaction_dirichlet"]) / scale

    # --- P1 절점 집합 진단 (§14.2) --------------------------------------
    rep["nset_faces"] = {n: dict(faces=len(f.items), area=f.area,
                                 unused_nodes=len(f.unused_nodes))
                         for n, f in A.faces.items()}
    # --- P2 물성 유효 범위 ------------------------------------------------
    warn = {}
    for e in range(mesh.ne):
        m = materials[str(mesh.emat[e])]
        if m.T_range is None:
            continue
        Te = T[mesh.elems[e]]
        if Te.min() < m.T_range[0] or Te.max() > m.T_range[1]:
            w = warn.setdefault(m.name, [1e30, -1e30])
            w[0] = min(w[0], float(Te.min()))
            w[1] = max(w[1], float(Te.max()))
    rep["material_range_violation"] = warn
    # --- P3 전도(곡선) 대 복사(직선) 형상 편차 ---------------------------
    #   전도는 요소의 곡선 변을 보고, 복사는 코너 두 점을 잇는 직선 원뿔대를
    #   본다.  두 형상이 다르므로 그 편차를 항상 보고한다.  1차 요소나 직선
    #   변에서는 정확히 0 이 되어야 한다.
    if len(S):
        from .assemble import _edge_area
        a_curved = np.array([_edge_area(mesh, int(e), int(le))
                             for e, le in zip(S.elem, S.ledge)])
        d = a_curved - S.area
        scale = np.maximum(a_curved, 1e-300)
        rep["P3_curved_area_total"] = float(a_curved.sum())
        rep["P3_straight_area_total"] = float(S.area.sum())
        rep["P3_area_rel_diff_total"] = float(
            abs(a_curved.sum() - S.area.sum()) / max(a_curved.sum(), 1e-300))
        rep["P3_area_rel_diff_max"] = float(np.abs(d / scale).max())
        rep["P3_worst_segment"] = int(np.argmax(np.abs(d / scale)))
    # --- 상세 출력용 배열 (USER_GUIDE 10.3) ------------------------------
    detail = {"nodal_residual": R.copy()}
    if len(S):
        Ts = 0.5 * (T[S.n1] + T[S.n2])
        T4 = Ts ** 4
        detail["segment_net_flux"] = (A.Mrad @ T4 - A.Drad * T4) / S.area
    rep["time_total_s"] = time.time() - t0
    if not converged:
        raise ConvergenceError(
            "최대 반복 %d 회에서 수렴하지 않았다 (증분 %.3e, 에너지 %.3e). "
            "AND 조건은 완화하지 않는다." % (itmax, hist[-1]["step"],
                                             hist[-1]["energy_imbalance"]))
    return T, S, B, rep, detail
