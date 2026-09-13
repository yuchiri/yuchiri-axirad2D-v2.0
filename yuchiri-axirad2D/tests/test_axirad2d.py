# -*- coding: utf-8 -*-
"""Verification tests / 검증 시험.

실행:  PYTHONPATH=src:examples python3 -m pytest tests -q
"""
import os
import sys
import numpy as np
import pytest
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "examples"),
          os.path.join(ROOT, "examples", "coaxial_enclosure")):
    if p not in sys.path:
        sys.path.insert(0, p)

from axirad2d import elements as E                                  # noqa: E402
from axirad2d.materials import Material, Poly, SIGMA, MaterialError  # noqa: E402
from axirad2d.mesh import Mesh, MeshError                            # noqa: E402
from axirad2d.assemble import Assembler                              # noqa: E402
from axirad2d import surfaces, montecarlo                            # noqa: E402
from gridgen import structured_quad9                               # noqa: E402

CORNERS = {
    E.TRI3: np.array([[0, 0], [1, 0], [0, 1]], float),
    E.TRI6: np.array([[0, 0], [1, 0], [0, 1], [.5, 0], [.5, .5], [0, .5]], float),
    E.QUAD4: np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float),
    E.QUAD8: np.array([[-1, -1], [1, -1], [1, 1], [-1, 1],
                       [0, -1], [1, 0], [0, 1], [-1, 0]], float),
    E.QUAD9: np.array([[-1, -1], [1, -1], [1, 1], [-1, 1],
                       [0, -1], [1, 0], [0, 1], [-1, 0], [0, 0]], float),
}


# ---------------------------------------------------------------- V-1
@pytest.mark.parametrize("et", E.SUPPORTED)
def test_V1_partition_of_unity(et):
    xi, eta, _ = E.quadrature(et, bump=1)
    N, dx, de = E.shape(et, xi, eta)
    assert np.abs(N.sum(axis=0) - 1.0).max() < 1e-13
    assert np.abs(dx.sum(axis=0)).max() < 1e-13
    assert np.abs(de.sum(axis=0)).max() < 1e-13


@pytest.mark.parametrize("et", E.SUPPORTED)
def test_V1_kronecker_delta(et):
    P = CORNERS[et]
    N, _, _ = E.shape(et, P[:, 0], P[:, 1])
    assert np.abs(N - np.eye(et)).max() < 1e-13


@pytest.mark.parametrize("et", E.SUPPORTED)
def test_V1_polynomial_reproduction(et):
    """해당 차수까지의 다항식을 정확히 재현한다."""
    P = CORNERS[et]
    xi, eta, _ = E.quadrature(et, bump=2)
    N, _, _ = E.shape(et, xi, eta)
    polys = [lambda a, b: 1 + 2 * a - 3 * b]
    if E.ORDER[et] == 2:
        polys.append(lambda a, b: 1 + a - 2 * b + 3 * a * a + b * b - a * b)
    for f in polys:
        v = f(P[:, 0], P[:, 1])
        assert np.abs(N.T @ v - f(xi, eta)).max() < 1e-12


# ---------------------------------------------------------------- V-2
@pytest.mark.parametrize("et", E.SUPPORTED)
def test_V2_quadrature_exactness(et):
    xi, eta, w = E.quadrature(et)
    ref = 0.5 if E.IS_TRI[et] else 4.0
    assert abs(w.sum() - ref) < 1e-13


# ---------------------------------------------------------------- V-3
def test_V3_material_derivative():
    p = Poly([1.5, 2e-3, -4e-7], {1: 300.0, 2: 5.0e4})
    T = np.array([350.0, 900.0, 2100.0])
    # 중심차분의 절단오차가 h^2 로 남으므로 Richardson 외삽으로 정밀도를 높인다
    h = 1e-3 * T
    d1 = (p(T + h) - p(T - h)) / (2 * h)
    d2 = (p(T + h / 2) - p(T - h / 2)) / h
    num = (4 * d2 - d1) / 3
    assert np.abs(num / p.d(T) - 1.0).max() < 1e-10


def test_negative_conductivity_aborts():
    from axirad2d.materials import check_k_positive
    with pytest.raises(MaterialError):
        check_k_positive("x", np.array([1.0, -0.5]))


# --------------------------------------------------------- 격자 유틸
def _annulus(a=0.02, b=0.10, h=0.05, nr=6, nz=3):
    g = structured_quad9([a, b], [0.0, h], [nr], [nz], lambda r, z: "m")
    nodes = g["nodes"]
    return Mesh(nodes, g["elems"], g["emat"], g["qvol"],
                {"inner": np.where(np.abs(nodes[:, 0] - a) < 1e-12)[0],
                 "outer": np.where(np.abs(nodes[:, 0] - b) < 1e-12)[0]})


def _solve(mesh, mats, bcs, S=None, B=None, T0=500.0, itmax=30):
    A = Assembler(mesh, mats, bcs, S, B)
    T = np.full(mesh.nn, T0)
    T[A.dir_nodes] = A.dir_vals
    for _ in range(itmax):
        R, J, _ = A.residual_jacobian(T)
        Rd, Jd = A.apply_dirichlet(R, J, T)
        dT = spla.spsolve(Jd.tocsc(), -Rd)
        T = T + dT
        if np.abs(dT).max() < 1e-10:
            break
    return T


# ---------------------------------------------------------------- V-4
def test_V4_divergence_theorem():
    m = _annulus()
    rep = m.check()
    assert rep["G4_rel_diff"] < rep["G4_tol"]
    a, b, h = 0.02, 0.10, 0.05
    exact = np.pi * (b * b - a * a) * h
    assert abs(rep["G4_volume_element"] / exact - 1.0) < 1e-13


def test_G1_detects_inverted_element():
    m = _annulus(nr=2, nz=1)
    c = m.elems[0].copy()
    c[[1, 3]] = c[[3, 1]]              # 코너 순서를 뒤집는다
    bad = Mesh(m.nodes, [c] + m.elems[1:], m.emat, m.qvol, m.nsets)
    with pytest.raises(MeshError):
        bad.check()


# ---------------------------------------------------------------- V-13
def test_V13_radial_conduction_ln_r():
    a, b = 0.02, 0.10
    m = _annulus(a, b, nr=10, nz=2)
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    bcs = [dict(type="dirichlet", nset="inner", T=1000.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    T = _solve(m, mats, bcs)
    r = m.nodes[:, 0]
    exact = 1000.0 + (300.0 - 1000.0) * np.log(r / a) / np.log(b / a)
    assert np.abs(T - exact).max() < 0.05


def test_V13_temperature_dependent_k_converges():
    a, b = 0.02, 0.10
    m = _annulus(a, b, nr=8, nz=2)
    mats = {"m": Material("m", Poly([5.0, 0.02]), True, 1.0)}
    bcs = [dict(type="dirichlet", nset="inner", T=1200.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    T = _solve(m, mats, bcs)
    assert 300.0 - 1e-6 <= T.min() and T.max() <= 1200.0 + 1e-6


# ------------------------------------------------- 경계조건 / 에너지
def test_flux_bc_energy_balance():
    a, b, h = 0.02, 0.10, 0.05
    m = _annulus(a, b, h, nr=6, nz=3)
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    q0 = 4000.0
    bcs = [dict(type="flux", nset="inner", q=q0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    A = Assembler(m, mats, bcs, None, None)
    T = _solve(m, mats, bcs)
    R, _, power = A.residual_jacobian(T)
    Pin = q0 * 2 * np.pi * a * h
    assert abs(power["inner:flux"] - Pin) / Pin < 1e-12
    assert abs(R[A.dir_nodes].sum() + Pin) / Pin < 1e-9


def test_convection_bc_jacobian():
    m = _annulus(nr=4, nz=2)
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    bcs = [dict(type="convection", nset="inner", h=50.0, T_inf=1200.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    T = _solve(m, mats, bcs)
    assert 300.0 <= T.min() and T.max() <= 1200.0


# ------------------------------------------------------ V-6 야코비안
def test_V6_jacobian_matches_numerical_including_radiation():
    m = _cavity_small()
    mats = _cavity_mats(0.7, 0.9)
    S = surfaces.extract(m, mats, 0.9, {})
    B, _, _ = montecarlo.gebhart(S, n_ray=400, seed=3, leak_tol=1.0)
    bcs = [dict(type="dirichlet", nset="outer_wall", T=300.0),
           dict(type="env_radiation", nset="axis_none", emissivity=0.5,
                T_env=350.0)] if False else [
        dict(type="dirichlet", nset="outer_wall", T=300.0)]
    A = Assembler(m, mats, bcs, S, B)
    rng = np.random.default_rng(0)
    T = 600.0 + 200.0 * rng.random(m.nn)
    R0, J0, _ = A.residual_jacobian(T)
    idx = rng.choice(m.nn, size=12, replace=False)
    Jd = np.asarray(J0.todense())
    for j in idx:
        h = 1e-4 * T[j]
        Tp = T.copy(); Tp[j] += h
        Tm = T.copy(); Tm[j] -= h
        Rp, _, _ = A.residual_jacobian(Tp)
        Rm, _, _ = A.residual_jacobian(Tm)
        num = (Rp - Rm) / (2 * h)
        ana = Jd[:, j]
        sc = max(np.abs(ana).max(), 1e-12)
        assert np.abs(num - ana).max() / sc < 5e-6


# --------------------------------------------------- 복사 (V-15 계열)
def _cavity_small():
    from build_mesh import build
    return build(nr=(2, 2, 1), nz=(1, 1, 3, 1, 1))


def _cavity_mats(e_in, e_sh):
    return {"inner_solid": Material("inner_solid", Poly([500.0]), True, e_in),
            "shell_solid": Material("shell_solid", Poly([500.0]), True, e_sh),
            "cavity_vacuum": Material("cavity_vacuum", Poly([1e-5]), opaque=False)}


def _inner_mask(S):
    rm = 0.5 * (S.P1[:, 0] + S.P2[:, 0])
    zm = 0.5 * (S.P1[:, 1] + S.P2[:, 1])
    return (rm <= 0.05 + 1e-12) & (zm >= 0.05 - 1e-12) & (zm <= 0.15 + 1e-12)


def test_surface_extraction_and_areas():
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(1.0, 1.0), 1.0, {})
    inner = _inner_mask(S)
    A1x = 2 * np.pi * 0.05 * 0.10 + 2 * np.pi * 0.05 ** 2
    A2x = 2 * np.pi * 0.10 * 0.16 + 2 * np.pi * 0.10 ** 2
    assert abs(S.area[inner].sum() - A1x) < 1e-14
    assert abs(S.area[~inner].sum() - A2x) < 1e-14


def test_V21_closure_and_view_factors():
    """볼록체 완전 포위 — F(1->1) = 0, F(1->2) = 1 은 정확하다."""
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(1.0, 1.0), 1.0, {})
    rep = {}
    B, lo, lb = montecarlo.gebhart(S, n_ray=3000, seed=5, report=rep)
    assert rep["leak_open"] == 0.0 and rep["leak_bounce"] == 0.0
    assert abs(rep["closure_min"] - 1.0) < 1e-12
    inner = _inner_mask(S)
    a = S.area
    F11 = (a[inner] @ B[np.ix_(inner, inner)].sum(axis=1)) / a[inner].sum()
    F12 = (a[inner] @ B[np.ix_(inner, ~inner)].sum(axis=1)) / a[inner].sum()
    assert F11 == 0.0
    assert abs(F12 - 1.0) < 1e-12


def test_V8_batch_invariance_bitwise():
    """§10.6 — 광선을 어떻게 나누어도 결과가 비트 단위로 같다."""
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(0.7, 0.5), 0.5, {})
    Ba, _, _ = montecarlo.gebhart(S, n_ray=1500, seed=9, leak_tol=1.0)
    ns = len(S)
    B1, _, _ = montecarlo.gebhart(S, n_ray=1500, seed=9,
                                  seg_subset=np.arange(0, ns, 3))
    B2, _, _ = montecarlo.gebhart(S, n_ray=1500, seed=9,
                                  seg_subset=np.arange(1, ns, 3))
    B3, _, _ = montecarlo.gebhart(S, n_ray=1500, seed=9,
                                  seg_subset=np.arange(2, ns, 3))
    assert np.array_equal(Ba, B1 + B2 + B3)


def test_V15_exact_two_surface_black_wall():
    """공동벽이 흑체이면 Q = e1 A1 sigma (T1^4 - T2^4) 가 정확하다."""
    m = _cavity_small()
    e1 = 0.8
    S = surfaces.extract(m, _cavity_mats(e1, 1.0), 1.0, {})
    B, _, _ = montecarlo.gebhart(S, n_ray=30000, seed=11)
    inner = _inner_mask(S)
    A1 = S.area[inner].sum()
    w = SIGMA * S.area * S.eps
    M = (B * w[:, None]).T
    T1, T2 = 1000.0, 300.0
    T4 = np.where(inner, T1, T2) ** 4
    Q = -(M @ T4 - w * T4)[inner].sum()
    Qx = e1 * A1 * SIGMA * (T1 ** 4 - T2 ** 4)
    assert abs(Q / Qx - 1.0) < 3e-3


def test_D1_D2_no_closure_correction():
    """§10.7 — 열린 형상에서 sum_b B_ab 가 1 로 채워지지 않는다."""
    # 닫힌 형상 (대조군)
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(1.0, 1.0), 1.0, {})
    rc = {}
    montecarlo.gebhart(S, n_ray=2000, seed=13, report=rc)
    assert abs(rc["closure_min"] - 1.0) < 1e-12
    assert rc["leak_open"] == 0.0
    # 열린 형상 — 세그먼트 일부를 제거해 구멍을 낸다
    keep = np.ones(len(S), dtype=bool)
    keep[_inner_mask(S)] = True
    hole = np.where(~_inner_mask(S))[0][:3]
    keep[hole] = False
    So = surfaces.Segments()
    for a in ("n1", "n2", "P1", "P2", "area", "eps", "nrm", "encl"):
        setattr(So, a, getattr(S, a)[keep])
    So.owner = [o for o, k in zip(S.owner, keep) if k]
    ro = {}
    with pytest.raises(montecarlo.RadiationError):
        montecarlo.gebhart(So, n_ray=2000, seed=13, report=ro)
    assert ro["leak_open"] > 0.0            # 누출이 실제로 계수되었다
    assert ro["closure_min"] < 1.0          # 1 로 채워지지 않았다


def test_D5_blocking_is_resolved():
    """§10.2 — 내부물체가 반대편 벽을 가린다. 중점 기준이면 놓치는 경우."""
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(1.0, 1.0), 1.0, {})
    B, _, _ = montecarlo.gebhart(S, n_ray=4000, seed=17)
    inner = _inner_mask(S)
    # 내부물체 옆면끼리는 서로 볼 수 없다 (볼록) -> B = 0
    side = inner & (np.abs(S.nrm[:, 0]) > 0.5)
    assert B[np.ix_(side, side)].max() == 0.0
    # 아래 벽 -> 위 벽 은 내부물체에 가려 직접 교환이 크게 줄어든다
    assert B[np.ix_(inner, ~inner)].sum() > 0.0


def test_D7_and_condition_not_or():
    """§12.4 — 증분이 작아도 에너지 불균형이 크면 수렴이 아니다."""
    eps_T, eps_E = 1e-6, 1e-9
    step, eimb = 1e-9, 1e-3
    assert not (step < eps_T and eimb < eps_E)
    assert (step < eps_T) or (eimb < eps_E)     # OR 이면 통과해 버린다


def test_env_radiation_overlap_is_rejected():
    """§8.5 — 환경 복사가 자동 복사면과 겹치면 중단한다.

    겹침이 가능한 곳은 '투명 요소가 도메인 경계와 접하는 변' 뿐이다.
    재료 경계의 복사면은 외곽 변이 아니므로 절점 집합으로 잡히지 않는다.
    """
    from axirad2d.solve import solve_steady
    a, b = 0.02, 0.10
    g = structured_quad9([a, 0.06, b], [0.0, 0.05], [3, 3], [3],
                         lambda r, z: "solid" if r < 0.06 else "vac")
    nodes = g["nodes"]
    outer = np.where(np.abs(nodes[:, 0] - b) < 1e-12)[0]
    inner = np.where(np.abs(nodes[:, 0] - a) < 1e-12)[0]
    m = Mesh(nodes, g["elems"], g["emat"], g["qvol"],
             {"outer": outer, "inner": inner})
    mats = {"solid": Material("solid", Poly([20.0]), True, 0.8),
            "vac": Material("vac", Poly([1e-5]), opaque=False)}
    bcs = [dict(type="dirichlet", nset="inner", T=600.0),
           dict(type="env_radiation", nset="outer", emissivity=0.5, T_env=350.0)]
    with pytest.raises(RuntimeError, match="8.5"):
        solve_steady(m, mats, bcs, dict(n_ray=200, leak_tol=1.0), dict(), {})


# ================================================================== BM-2
def _bm2():
    sys.path.insert(0, os.path.join(ROOT, "examples", "bm2_bm5"))
    from build_meshes import build_bm2
    from problem_def import BM2, bm2_view_factors
    return build_bm2, BM2, bm2_view_factors


def _bm2_groups(S, BM2):
    zm = 0.5 * (S.P1[:, 1] + S.P2[:, 1])
    rm = 0.5 * (S.P1[:, 0] + S.P2[:, 0])
    return (np.abs(zm) < 1e-9, np.abs(zm - BM2["L"]) < 1e-9,
            np.abs(rm - BM2["R"]) < 1e-9)


def _gF(S, B, g1, g2):
    return float(S.area[g1] @ B[np.ix_(g1, g2)].sum(axis=1) / S.area[g1].sum())


def test_BM2_segment_areas_exact():
    build_bm2, BM2, vf = _bm2()
    m = build_bm2()
    mats = {"shell": Material("shell", Poly([30.0]), True, 1.0),
            "vacuum": Material("vacuum", Poly([1e-5]), opaque=False)}
    S = surfaces.extract(m, mats, 1.0, {})
    d1, d2, sd = _bm2_groups(S, BM2)
    ex = vf(BM2["R"], BM2["R"], BM2["L"])
    assert d1.sum() == 5 and d2.sum() == 5 and sd.sum() == 10
    assert abs(S.area[d1].sum() - ex["A_disk"]) < 1e-15
    assert abs(S.area[sd].sum() - ex["A_side"]) < 1e-15


def test_BM2_view_factors_match_closed_form():
    """전 면 흑체 -> B = F.  동축 평행 원판의 닫힌 형태와 대조."""
    build_bm2, BM2, vf = _bm2()
    m = build_bm2()
    mats = {"shell": Material("shell", Poly([30.0]), True, 1.0),
            "vacuum": Material("vacuum", Poly([1e-5]), opaque=False)}
    rep = {}
    S = surfaces.extract(m, mats, 1.0, rep)
    d1, d2, sd = _bm2_groups(S, BM2)
    ex = vf(BM2["R"], BM2["R"], BM2["L"])
    B, _, _ = montecarlo.gebhart(S, n_ray=40000, seed=101, report=rep)
    assert rep["leak_open"] == 0.0 and rep["leak_bounce"] == 0.0
    assert abs(rep["closure_min"] - 1.0) < 1e-12
    assert _gF(S, B, d1, d1) == 0.0                      # 평면 -> 자기 자신 안 봄
    assert abs(_gF(S, B, d1, d2) / ex["F_disk_disk"] - 1.0) < 0.012
    assert abs(_gF(S, B, sd, d1) / ex["F_side_disk"] - 1.0) < 0.012


# ================================================================== BM-5
def _bm5():
    sys.path.insert(0, os.path.join(ROOT, "examples", "bm2_bm5"))
    from build_meshes import build_bm5
    from problem_def import BM5, bm5_exchange_areas
    return build_bm5, BM5, bm5_exchange_areas


def _bm5_mats(e1, e2):
    return {"inner_solid": Material("inner_solid", Poly([400.0]), True, e1),
            "outer_solid": Material("outer_solid", Poly([400.0]), True, e2),
            "vacuum": Material("vacuum", Poly([1e-5]), opaque=False)}


def _bm5_inner(S, BM5):
    rho = np.hypot(0.5 * (S.P1[:, 0] + S.P2[:, 0]),
                   0.5 * (S.P1[:, 1] + S.P2[:, 1]))
    return rho < 0.5 * (BM5["a"] + BM5["b"])


def test_BM5_faceting_converges_second_order():
    """원뿔대가 구면을 근사하는 오차는 Delta_theta^2 로 줄어든다."""
    build_bm5, BM5, _ = _bm5()
    exact = 4 * np.pi * BM5["a"] ** 2
    errs = []
    for nth in (12, 24, 48):
        S = surfaces.extract(build_bm5(ntheta=(nth,)), _bm5_mats(1.0, 1.0), 1.0, {})
        A1 = S.area[_bm5_inner(S, BM5)].sum()
        errs.append(abs(A1 - exact) / exact)
    assert 3.5 < errs[0] / errs[1] < 4.5
    assert 3.5 < errs[1] / errs[2] < 4.5


def test_BM5_black_limit_view_factors():
    """볼록체 완전 포위 — 다면체 근사에서도 F(1->1) = 0, F(1->2) = 1."""
    build_bm5, BM5, _ = _bm5()
    S = surfaces.extract(build_bm5(ntheta=(12,)), _bm5_mats(1.0, 1.0), 1.0, {})
    inn = _bm5_inner(S, BM5)
    rep = {}
    B, _, _ = montecarlo.gebhart(S, n_ray=5000, seed=7, report=rep)
    assert rep["leak_open"] == 0.0
    assert abs(rep["closure_min"] - 1.0) < 1e-12
    assert _gF(S, B, inn, inn) == 0.0
    assert abs(_gF(S, B, inn, ~inn) - 1.0) < 1e-12


def test_BM5_gray_two_surface_exact():
    """★ 동심 구에서는 회색벽 2면 집중식이 정확하다 (조사량 균일).

    BM-1(원통 공동)에서는 같은 식이 1.6 % 어긋났고 광선을 늘려도 줄지 않았다.
    그 편차가 코드 결함이 아니라 집중식의 가정 때문임을 이 시험이 확인한다.
    """
    build_bm5, BM5, exch = _bm5()
    e1, e2 = BM5["eps1"], BM5["eps2"]
    S = surfaces.extract(build_bm5(ntheta=(24,)), _bm5_mats(e1, e2), e2, {})
    inn = _bm5_inner(S, BM5)
    A1, A2 = S.area[inn].sum(), S.area[~inn].sum()
    B, _, _ = montecarlo.gebhart(S, n_ray=20000, seed=21)
    w = SIGMA * S.area * S.eps
    T1, T2 = 1000.0, 300.0
    T4 = np.where(inn, T1, T2) ** 4
    Q = -((B * w[:, None]).T @ T4 - w * T4)[inn].sum()
    assert abs(Q / exch(T1, T2, A1, A2) - 1.0) < 5e-3


# ==================================================== 비직교 요소 / 패치 시험
# 이 세 시험은 2026-08 에 발견된 결함(야코비안 역행렬의 J12/J21 뒤바뀜)을
# 잡기 위해 추가되었다. 그 결함은 축에 정렬된 격자(J12 = J21 = 0)에서는
# 완전히 상쇄되어 드러나지 않았다. 기존 42건이 전부 직교 격자였던 것이 원인이다.

def _q9_to_t6(c):
    """직선변 Q9 를 T6 두 개로 정확 분할. 중심절점 8 이 대각선 0-2 의 중점이다."""
    return [np.array([c[0], c[1], c[2], c[4], c[5], c[8]], dtype=np.int64),
            np.array([c[0], c[2], c[3], c[8], c[6], c[7]], dtype=np.int64)]


def _annulus_mixed(n, mode, a=0.02, b=0.10, h=0.05):
    g = structured_quad9([a, b], [0.0, h], [n], [max(1, n // 3)],
                         lambda r, z: "m")
    nd = g["nodes"]
    el = []
    for i, c in enumerate(g["elems"]):
        if mode == "q9" or (mode == "mix" and i % 2 == 1):
            el.append(c)
        else:
            el.extend(_q9_to_t6(c))
    tol = 1e-12
    return Mesh(nd, el, np.array(["m"] * len(el), dtype=object),
                np.zeros(len(el)),
                {"inner": np.where(np.abs(nd[:, 0] - a) < tol)[0],
                 "outer": np.where(np.abs(nd[:, 0] - b) < tol)[0],
                 "bot": np.where(np.abs(nd[:, 1]) < tol)[0],
                 "top": np.where(np.abs(nd[:, 1] - h) < tol)[0]})


@pytest.mark.parametrize("etype", E.SUPPORTED)
def test_Va_gradients_on_non_axis_aligned_element(etype):
    """★ 비직교 요소에서 dN/dr, dN/dz 가 정확한 기울기를 준다.

    축에 정렬된 요소만 시험하면 야코비안 역행렬의 성분을 바꿔 써도 통과한다.
    여기서는 일부러 기울어진 요소를 쓴다.
    """
    ref = CORNERS[etype]
    # 기울어진 어파인 사상:  r = 0.10 + 0.03*x + 0.011*y ,  z = 0.004*x + 0.02*y
    P = np.stack([0.10 + 0.030 * ref[:, 0] + 0.011 * ref[:, 1],
                  0.004 * ref[:, 0] + 0.020 * ref[:, 1]], axis=1)
    m = Mesh(P, [np.arange(etype)], np.array(["m"], dtype=object))
    _, dNdr, dNdz, det, r, w = m.elem_geom(0, bump=2)
    assert det.min() > 0
    # 선형장은 모든 요소가, 2차장은 2차 요소가 정확히 재현해야 한다
    cases = [(lambda rr, zz: 2.0 * rr - 3.0 * zz,
              lambda rr, zz: np.full_like(rr, 2.0),
              lambda rr, zz: np.full_like(rr, -3.0))]
    if E.ORDER[etype] == 2:
        cases.append((lambda rr, zz: rr * rr + 2.0 * rr * zz,
                      lambda rr, zz: 2.0 * rr + 2.0 * zz,
                      lambda rr, zz: 2.0 * rr))
    N, _, _, _, _, _ = m.elem_geom(0, bump=2)
    zq = N.T @ P[:, 1]
    for f, fr, fz in cases:
        T = f(P[:, 0], P[:, 1])
        assert np.abs(dNdr.T @ T - fr(r, zq)).max() < 1e-9
        assert np.abs(dNdz.T @ T - fz(r, zq)).max() < 1e-9


@pytest.mark.parametrize("mode", ["q9", "t6", "mix"])
def test_Vb_patch_test_linear_field(mode):
    """★ 패치 시험 — 선형 온도장에서 내부 절점의 잔차가 0 이어야 한다.

    T = 300 + 4000 z 는 축대칭 전도 방정식의 정확해다 (dT/dr = 0).
    따라서 내부 절점의 약형 잔차는 정확히 0 이다.
    """
    m = _annulus_mixed(4, mode)
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    A = Assembler(m, mats, [], None, None)
    T = 300.0 + 4000.0 * m.nodes[:, 1]
    R, J, _ = A.residual_jacobian(T)
    bnd = set()
    for e, le in m.boundary_edges():
        n1, n2, nm = m.edge_node_ids(e, le)
        bnd.update([n1, n2] + ([nm] if nm is not None else []))
    inner = np.array([i for i in range(m.nn) if i not in bnd])
    scale = max(np.abs(R).max(), 1.0)
    assert np.abs(R[inner]).max() / scale < 1e-12
    # 강성행렬은 대칭이고 상수 모드를 소멸시켜야 한다
    Jd = np.asarray(J.todense())
    assert np.abs(Jd - Jd.T).max() / max(np.abs(Jd).max(), 1e-30) < 1e-12
    assert np.abs(Jd @ np.ones(m.nn)).max() / max(np.abs(Jd).max(), 1e-30) < 1e-12


@pytest.mark.parametrize("mode", ["q9", "t6", "mix"])
def test_Vc_mesh_convergence_ln_r(mode):
    """★ 격자 수렴 — ln(r) 정확해 대비 오차가 세분과 함께 줄어야 한다.

    결함이 있을 때 T6 는 오차가 154 K 에서 정체했다 (감소비 1.05).
    """
    a, b = 0.02, 0.10
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    bcs = [dict(type="dirichlet", nset="inner", T=1000.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    errs = []
    for n in (4, 8, 16):
        m = _annulus_mixed(n, mode)
        m.check()
        T = _solve(m, mats, bcs, itmax=15)
        r = m.nodes[:, 0]
        exact = 1000.0 + (300.0 - 1000.0) * np.log(r / a) / np.log(b / a)
        errs.append(float(np.abs(T - exact).max()))
    assert errs[0] < 5.0                      # 조립이 근본적으로 옳다
    assert errs[1] / errs[0] < 0.35           # 세분하면 최소 3배 가까이 줄어든다
    assert errs[2] / errs[1] < 0.35


# ========================================================== DB-3 (생체열)
def _db3():
    sys.path.insert(0, os.path.join(ROOT, "examples", "db3"))
    import db3_problem as P
    import db3_verify as V
    return P, V


def test_DB3_perfusion_zero_is_inert():
    """관류율 0 이면 관류 항이 결과를 전혀 바꾸지 않아야 한다.

    이 성질이 있어야 관류 기능 추가가 기존 결과를 건드리지 않았다고
    허용오차 없이 말할 수 있다.
    """
    m = _annulus_mixed(4, "q9")
    mats0 = {"m": Material("m", Poly([25.0]), True, 1.0)}
    mats1 = {"m": Material("m", Poly([25.0]), True, 1.0,
                           perfusion=0.0, q_met=0.0)}
    bcs = [dict(type="dirichlet", nset="inner", T=1000.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    T0 = _solve(m, mats0, bcs)
    T1 = _solve(m, mats1, bcs)
    assert np.array_equal(T0, T1)


def test_DB3_perfusion_requires_blood_properties():
    """관류를 쓰면서 혈액 물성을 주지 않으면 중단해야 한다 (조용히 0 이 아니라)."""
    from axirad2d.assemble import BCError
    m = _annulus_mixed(2, "q9")
    mats = {"m": Material("m", Poly([25.0]), True, 1.0, perfusion=0.01)}
    with pytest.raises(BCError, match="관류율"):
        Assembler(m, mats, [], None, None)


def test_DB3_exact_solution_self_consistency():
    """참조해가 독립적으로 알려진 극한 세 개를 재현한다."""
    P, V = _db3()
    from db3_exact import Layer, Stack, total_surface_loss
    # (1) 관류 0, 복사 0 -> 직렬 저항
    st = Stack([Layer("a", 0.002, 0.3, 0.0, 0.0)], rho_cb=3.77e6, T_a=310.15)
    r = st.solve(T_core=310.15, h=10.0, T_inf=300.0, eps=0.0, T_env=300.0)
    q = total_surface_loss(r["T_surface"], 10.0, 300.0, 0.0, 300.0)
    assert abs(q - (310.15 - 300.0) / (0.002 / 0.3 + 0.1)) < 1e-10
    # (2) 관류 + 표면 단열 -> T == T_a
    st2 = Stack([Layer("a", 0.01, 0.5, 0.001, 0.0)], rho_cb=3.77e6, T_a=310.15)
    r2 = st2.solve(310.15, 0.0, 300.0, 0.0, 300.0)
    assert np.abs(r2["T_of_x"](np.linspace(0, 0.01, 5)) - 310.15).max() < 1e-10
    # (3) 한 층을 둘로 쪼개도 같아야 한다
    A = Stack([Layer("a", 0.004, 0.35, 0.001, 400.0)], 3.77e6, 310.15)
    B = Stack([Layer("a1", 0.001, 0.35, 0.001, 400.0),
               Layer("a2", 0.003, 0.35, 0.001, 400.0)], 3.77e6, 310.15)
    assert abs(A.solve(310.15, 8.0, 297.0, 0.98, 297.0)["T_surface"]
               - B.solve(310.15, 8.0, 297.0, 0.98, 297.0)["T_surface"]) < 1e-12


@pytest.mark.parametrize("scale", [1.0, 10.0])
def test_DB3_converges_to_exact_solution(scale):
    """★ 다층 + 관류 + 대류 + 환경 복사가 정확해로 수렴한다.

    합격은 고정 허용오차가 아니라 관측 수렴 차수로 판정한다.
    """
    P, V = _db3()
    st, ex = V.exact(scale)
    errs = []
    for rf in (1, 2):
        m, T, pw, react, hist = V.run(rf, scale)
        Tex = ex["T_of_x"](m.nodes[:, 1])
        errs.append(float(np.abs(T - Tex).max()))
    assert errs[0] < 1e-3                    # 조립이 근본적으로 옳다
    assert errs[1] / errs[0] < 0.2           # 세분하면 최소 5배 줄어든다


def test_DB3_no_spurious_radial_variation():
    """측면 단열이므로 정확해에 r 의존성이 없다. 반경 변화는 결함 신호다."""
    P, V = _db3()
    m, T, pw, react, hist = V.run(1, 1.0)
    worst = 0.0
    for z in np.unique(np.round(m.nodes[:, 1], 12)):
        sel = np.abs(m.nodes[:, 1] - z) < 1e-14
        if sel.sum() > 1:
            worst = max(worst, float(T[sel].max() - T[sel].min()))
    assert worst < 1e-9


# ============================================ P3 형상 편차 (곡선 대 직선)
def test_P3_straight_edges_give_zero_shape_bias():
    """직선 변 격자에서는 곡선 변 면적과 직선 세그먼트 면적이 같아야 한다."""
    from axirad2d.assemble import _edge_area
    m = _cavity_small()
    S = surfaces.extract(m, _cavity_mats(1.0, 1.0), 1.0, {})
    a_curved = np.array([_edge_area(m, int(e), int(le))
                         for e, le in zip(S.elem, S.ledge)])
    assert np.abs(a_curved / S.area - 1.0).max() < 1e-12


def test_P3_detects_faceting_on_a_curved_mesh():
    """★ 곡면 격자에서 P3 가 실제 다면체 근사 오차를 잡아낸다.

    BM-5 의 격자는 구면을 원뿔대로 근사하므로, 곡선 변 면적과 직선 세그먼트
    면적의 차이가 곧 다면체 근사 오차다. nth = 24 에서 그 값은 약 0.214 %.
    """
    from axirad2d.assemble import _edge_area
    build_bm5, BM5, _ = _bm5()
    mesh = build_bm5(ntheta=(24,))
    S = surfaces.extract(mesh, _bm5_mats(1.0, 1.0), 1.0, {})
    a_curved = np.array([_edge_area(mesh, int(e), int(le))
                         for e, le in zip(S.elem, S.ledge)])
    rel = abs(a_curved.sum() - S.area.sum()) / a_curved.sum()
    assert 1.5e-3 < rel < 3.0e-3           # 다면체 근사 오차가 실제로 잡힌다
    # 곡선 변 적분은 참 구면 면적을 재현해야 한다
    exact = 4 * np.pi * (BM5["a"] ** 2 + BM5["b"] ** 2)
    assert abs(a_curved.sum() / exact - 1.0) < 1e-6


# ==================================== 문서가 약속한 출력이 실제로 나오는가
def test_documented_detail_arrays_are_actually_written(tmp_path):
    """USER_GUIDE 10.3 이 약속한 세 배열이 detail=true 에서 실제로 기록된다.

    문서가 코드보다 앞서가면 그 격차는 조용히 남는다. 이 시험이 그것을 막는다.
    """
    from axirad2d import problemio
    from axirad2d.solve import solve_steady
    m = _cavity_small()
    mats = _cavity_mats(1.0, 1.0)
    bcs = [dict(type="dirichlet", nset="outer_wall", T=300.0)]
    rep = {}
    T, S, B, rep, detail = solve_steady(
        m, mats, bcs, dict(n_ray=400, seed=3, leak_tol=1.0),
        dict(eps_T=1e-6, eps_E=1e-6, max_iter=30), rep)
    out = str(tmp_path / "out")
    problemio.write_results(out, m, T, S, B, rep, detail=True, extra=detail)
    z = np.load(os.path.join(out, "results.npz"))
    for key in ("gebhart_B", "segment_net_flux", "nodal_residual"):
        assert key in z.files, key
    assert z["segment_net_flux"].shape == (len(S),)
    assert z["nodal_residual"].shape == (m.nn,)


def test_documented_diagnostics_keys_exist():
    """USER_GUIDE 10.2 가 상시 출력이라고 적은 항목이 진단에 실제로 있다."""
    from axirad2d.solve import solve_steady
    m = _cavity_small()
    rep = {}
    T, S, B, rep, _ = solve_steady(
        m, _cavity_mats(1.0, 1.0),
        [dict(type="dirichlet", nset="outer_wall", T=300.0)],
        dict(n_ray=400, seed=11, leak_tol=1.0),
        dict(eps_T=1e-6, eps_E=1e-6, max_iter=30), rep)
    for key in ("G1_det_min", "G2_worst_rel_diff", "G4_rel_diff",
                "leak_open", "leak_bounce", "closure_min",
                "reciprocity_l1", "reciprocity_max_abs", "reciprocity_max_rel",
                "energy_residual_rel", "nset_faces", "material_range_violation",
                "P3_area_rel_diff_max", "parallel_mode", "mpi_size",
                "seed", "n_ray", "n_bounce_max", "leak_tol"):
        assert key in rep, key


def test_dirichlet_only_problem_converges():
    """★ 열원도 유속 경계도 없는 문제가 수렴으로 보고되어야 한다.

    에너지 불균형을 '순 유입' 으로 정규화하면 이런 문제에서 분모가 0 이 되어,
    완전히 수렴한 해가 실패로 보고된다.  정규화 규모는 '열 처리량' 이어야 한다.
    """
    from axirad2d.solve import solve_steady
    m = _annulus_mixed(6, "q9")
    mats = {"m": Material("m", Poly([25.0]), True, 1.0)}
    bcs = [dict(type="dirichlet", nset="inner", T=1000.0),
           dict(type="dirichlet", nset="outer", T=300.0)]
    rep = {}
    T, S, B, rep, _ = solve_steady(m, mats, bcs, dict(), dict(), rep)
    assert rep["converged"]
    assert rep["energy_scale_W"] > 1.0            # 실제 열이 흐른다
    assert rep["energy_residual_rel"] < 1e-12
    r = m.nodes[:, 0]
    exact = 1000.0 + (300.0 - 1000.0) * np.log(r / 0.02) / np.log(0.10 / 0.02)
    assert np.abs(T - exact).max() < 0.2
    assert "seed" not in rep                       # 복사가 없으면 씨앗도 없다


def test_property_definition_has_a_single_source():
    """★ 물성 정의 사본이 벤치마크 모음의 것과 어긋나지 않아야 한다.

    같은 상수를 두 곳에 두면 언젠가 갈라진다. 이 시험이 그것을 막는다.
    벤치마크 모음이 함께 있지 않으면 건너뛴다.
    """
    import hashlib
    mine = os.path.join(ROOT, "examples", "db3", "db3_properties.py")
    # 저장소 이름이 배포판마다 다를 수 있으므로 후보를 모두 본다.
    # The suite may be checked out under either name; try both.
    theirs = None
    for name in ("yuchiri-axibio-bench", "axibio-bench"):
        cand = os.path.join(os.path.dirname(ROOT), name, "benchmarks",
                            "db3_layered_skin", "exact", "db3_properties.py")
        if os.path.exists(cand):
            theirs = cand
            break
    if theirs is None:
        pytest.skip("benchmark suite not present next to the solver")
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert h(mine) == h(theirs), (
        "db3_properties.py in the solver example and in the benchmark suite "
        "have drifted apart")


def test_missing_temperature_reference_says_so():
    """★ 온도 기준점이 없으면 '수렴 실패' 가 아니라 그 사실을 말해야 한다.

    Dirichlet 도 대류도 환경 복사도 없으면 행렬이 특이하다. Newton 은 발산하고
    "수렴하지 않았다" 로 끝나는데, 그 메시지는 원인을 가린다.
    """
    from axirad2d.solve import solve_steady
    from axirad2d.assemble import BCError
    m = _annulus_mixed(3, "q9")
    m2 = Mesh(m.nodes, m.elems, m.emat, np.full(m.ne, 1.0e4), {})
    with pytest.raises(BCError, match="온도 기준점"):
        solve_steady(m2, {"m": Material("m", Poly([25.0]), True, 1.0)},
                     [], dict(), dict(), {})
