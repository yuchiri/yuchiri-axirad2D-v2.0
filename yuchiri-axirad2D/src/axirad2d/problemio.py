# -*- coding: utf-8 -*-
"""[EN] Input and output: reading the problem TOML, writing results and diagnostics.

Specification sections 4 and 14.

[KO] 입출력 — 문제 TOML 읽기, 결과와 진단 쓰기.

See USER_GUIDE sections 3 and 10 (problem file, output).
공개 문서 USER_GUIDE 3·10장 참조.
"""
from __future__ import annotations
import json
import os
try:                                    # Python 3.11 and newer
    import tomllib
except ModuleNotFoundError:             # Python 3.9 / 3.10: pip install tomli
    try:
        import tomli as tomllib
    except ModuleNotFoundError as _exc:
        raise ModuleNotFoundError(
            "TOML 을 읽을 모듈이 없다. Python 3.11 이상을 쓰거나 "
            "'pip install tomli' 를 하라. / No TOML reader: use Python 3.11+ "
            "or 'pip install tomli'.") from _exc
import numpy as np
from .materials import Material, Poly, MaterialError
from .mesh import load_npz

SCHEMA = "1.0"
_BC_TYPES = ("dirichlet", "flux", "adiabatic", "convection", "env_radiation")


class InputError(Exception):
    pass


def _poly(d, key):
    pos = d.get(key + "_pos", [])
    neg = d.get(key + "_neg", {})
    return Poly(pos, neg)


def read_problem(path):
    with open(path, "rb") as f:
        p = tomllib.load(f)
    if str(p.get("schema_version", SCHEMA)) != SCHEMA:
        raise InputError("schema_version 이 %s 가 아니다" % SCHEMA)
    base = os.path.dirname(os.path.abspath(path))
    if "mesh_file" not in p:
        raise InputError("mesh_file 이 없다")
    mesh_path = os.path.join(base, p["mesh_file"])
    lu = float(p.get("length_unit", 1.0))
    mesh = load_npz(mesh_path, lu)

    fp = mesh.fingerprint()
    given = p.get("mesh_hash")
    if given and str(given) != fp:                    # §4.2
        raise InputError("격자 지문 불일치 — 문제 파일 %s, 실제 %s" % (given, fp))

    mats = {}
    for name, d in p.get("material", {}).items():
        k = _poly(d, "k")
        if k.is_zero():
            raise InputError("재료 '%s' 의 k 계수가 비어 있다" % name)
        rho = _poly(d, "rho")
        cp = _poly(d, "cp")
        try:
            mats[name] = Material(
                name, k, opaque=bool(d.get("opaque", True)),
                emissivity=d.get("emissivity"),
                rho=None if rho.is_zero() else rho,
                cp=None if cp.is_zero() else cp,
                T_range=d.get("T_range"),
                perfusion=float(d.get("perfusion", 0.0)),
                q_met=float(d.get("q_met", 0.0)))
        except MaterialError as exc:
            raise InputError(str(exc)) from None
    missing = sorted({str(m) for m in mesh.emat} - set(mats))
    if missing:
        raise InputError("격자가 참조하는 재료가 정의되지 않았다: %s" % missing)

    bcs = []
    for name, d in p.get("bc", {}).items():
        t = d.get("type")
        if t not in _BC_TYPES:
            raise InputError("경계조건 '%s' 의 type 이 잘못되었다: %r "
                             "(허용 %s)" % (name, t, list(_BC_TYPES)))
        nset = d.get("nset", name)
        if nset not in mesh.nsets:
            raise InputError("경계조건 '%s' 의 절점 집합 '%s' 이 격자에 없다"
                             % (name, nset))
        bc = dict(d)
        bc["name"] = name
        bc["nset"] = nset
        for need, keys in (("dirichlet", ("T",)), ("flux", ("q",)),
                           ("convection", ("h", "T_inf")),
                           ("env_radiation", ("emissivity", "T_env"))):
            if t == need:
                for k in keys:
                    if k not in bc:
                        raise InputError("경계조건 '%s'(%s) 에 '%s' 가 없다"
                                         % (name, t, k))
        bcs.append(bc)
    if not any(b["type"] == "dirichlet" for b in bcs):
        # §8.4 — 경고. 중단하지는 않는다
        print("[경고] Dirichlet 경계조건이 없다. 정상상태 해가 유일하지 않을 수 있다.")

    # --- 혈액 물성 (Pennes 관류 항) ---------------------------------
    # 조직이 아니라 혈액의 성질이므로 문제 수준에 둔다.
    blood = p.get("blood")
    if blood is not None:
        for key in ("rho_cb", "T_arterial"):
            if key not in blood:
                raise InputError("[blood] 에 '%s' 가 없다" % key)
        blood = dict(rho_cb=float(blood["rho_cb"]),
                     T_arterial=float(blood["T_arterial"]))
    if any(m.perfusion > 0.0 for m in mats.values()) and blood is None:
        raise InputError(
            "관류율이 0 이 아닌 재료가 있으나 [blood] 절이 없다. "
            "rho_cb [J/(m^3 K)] 와 T_arterial [K] 이 필요하다.")

    analysis = p.get("analysis", {})
    if str(analysis.get("mode", "steady")) != "steady":
        raise InputError("현재 구현은 mode='steady' 만 지원한다. "
                         "과도 해석은 미구현이다 (README 구현 현황 참조).")
    solver = dict(p.get("solver", {}))
    solver["parallel"] = str(analysis.get("parallel", "serial"))
    return dict(mesh=mesh, materials=mats, bcs=bcs, blood=blood,
                radiation=p.get("radiation", {}), solver=solver,
                output=p.get("output", {}), mesh_hash=fp, raw=p)


# ----------------------------------------------------------------------
def _jsonify(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {str(k): _jsonify(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonify(v) for v in o]
    return o


def write_results(outdir, mesh, T, S, B, rep, detail=False, extra=None):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "diagnostics.json"), "w", encoding="utf-8") as f:
        json.dump(_jsonify(rep), f, ensure_ascii=False, indent=2)
    arrays = dict(nodes=mesh.nodes, T=T)
    if S is not None and len(S):
        Ts = 0.5 * (T[S.n1] + T[S.n2])
        arrays.update(seg_P1=S.P1, seg_P2=S.P2, seg_area=S.area,
                      seg_eps=S.eps, seg_encl=S.encl, seg_T=Ts)
        if detail:
            arrays["gebhart_B"] = B
    if detail and extra:
        # 상세 출력 — 켰을 때만 기록한다 (USER_GUIDE 10.3)
        for k, v in extra.items():
            if v is not None:
                arrays[k] = v
    np.savez_compressed(os.path.join(outdir, "results.npz"), **arrays)
    with open(os.path.join(outdir, "temperature.csv"), "w", encoding="utf-8") as f:
        f.write("node_id,r_m,z_m,T_K\n")
        for i, (r, z) in enumerate(mesh.nodes):
            f.write("%d,%.12g,%.12g,%.10g\n" % (i, r, z, T[i]))
    return outdir


def summary_text(rep) -> str:
    L = []
    A = L.append
    A("=" * 68)
    A("yuchiri-axirad2D 결과 요약 / results summary")
    A("=" * 68)
    A("격자   절점 검사: 중복 %s" % rep.get("duplicate_nodes"))
    A("  G1 det(J) 최소      = %.6e   (> 0 이어야 한다)" % rep.get("G1_det_min", float("nan")))
    A("  G2 면적 최대 상대차 = %.3e" % rep.get("G2_worst_rel_diff", float("nan")))
    A("  G4 부피  요소적분   = %.15e m^3" % rep.get("G4_volume_element", float("nan")))
    A("     발산정리 표면적분 = %.15e m^3" % rep.get("G4_volume_boundary", float("nan")))
    A("     상대차 %.3e   허용 %.3e" % (rep.get("G4_rel_diff", float("nan")),
                                        rep.get("G4_tol", float("nan"))))
    A("-" * 68)
    A("복사   enclosure %d 개  세그먼트 %d 개  면적 %s"
      % (rep.get("enclosure_count", 0), rep.get("segment_count", 0),
         ["%.6f" % a for a in rep.get("enclosure_area", [])]))
    A("  법선 교차검증 불일치 = %d 건" % len(rep.get("normal_mismatch", [])))
    A("  광선 %d   누출: 열린형상 %.3e  반사초과 %.3e"
      % (rep.get("n_ray", 0), rep.get("leak_open", 0.0), rep.get("leak_bounce", 0.0)))
    A("  폐쇄성 sum_b B_ab in [%.8f, %.8f]  (보정하지 않는다)"
      % (rep.get("closure_min", float("nan")), rep.get("closure_max", float("nan"))))
    A("  상반성  L1 %.4e   max_abs %.4e   max_rel %.4e"
      % (rep.get("reciprocity_l1", float("nan")),
         rep.get("reciprocity_max_abs", float("nan")),
         rep.get("reciprocity_max_rel", float("nan"))))
    A("  음의 B 성분 = %d" % rep.get("negative_B", 0))
    A("-" * 68)
    A("수렴   %s   반복 %d 회" % ("성공" if rep.get("converged") else "실패",
                                  len(rep.get("iterations", []))))
    for h in rep.get("iterations", [])[-6:]:
        A("   it %2d  |dT|/span %.3e   에너지불균형 %.3e   T [%.2f, %.2f]"
          % (h["iter"], h["step"], h["energy_imbalance"], h["Tmin"], h["Tmax"]))
    A("-" * 68)
    A("에너지 수지  (Pennes: 발열 + 대사 + 관류순 + 경계 = 유출)")
    for k, v in rep.get("power", {}).items():
        A("   %-28s %+.9g W" % (k, v))
    A("   %-28s %+.9g W" % ("Dirichlet 반력", rep.get("reaction_dirichlet", float("nan"))))
    A("   %-28s %+.9g W" % ("정규화 규모 (열 처리량)", rep.get("energy_scale_W", float("nan"))))
    A("   %-28s %.3e" % ("상대 잔차", rep.get("energy_residual_rel", float("nan"))))
    A("-" * 68)
    A("절점 집합 (P1)")
    for n, d in rep.get("nset_faces", {}).items():
        A("   %-16s 변 %4d  면적 %.8f m^2  미사용 절점 %d"
          % (n, d["faces"], d["area"], d["unused_nodes"]))
    A("물성 유효 범위 이탈 (P2): %s" % (rep.get("material_range_violation") or "없음"))
    if "P3_area_rel_diff_max" in rep:
        A("형상 편차 (P3) 전도(곡선) 대 복사(직선) 세그먼트 면적")
        A("   총면적  곡선 %.9f m^2  직선 %.9f m^2   상대차 %.2e"
          % (rep["P3_curved_area_total"], rep["P3_straight_area_total"],
             rep["P3_area_rel_diff_total"]))
        A("   세그먼트별 최대 상대차 %.2e  (세그먼트 %d)"
          % (rep["P3_area_rel_diff_max"], rep["P3_worst_segment"]))
    if "seed" in rep:
        A("병렬 %s (프로세스 %s)   난수 씨앗 %s   최대 반사 %s   leak_tol %s"
          % (rep.get("parallel_mode"), rep.get("mpi_size"), rep["seed"],
             rep["n_bounce_max"], rep["leak_tol"]))
    else:
        A("병렬 %s (프로세스 %s)   복사면이 없어 몬테카를로를 실행하지 않았다"
          % (rep.get("parallel_mode"), rep.get("mpi_size")))
    A("소요  복사 %.1f s   전체 %.1f s"
      % (rep.get("time_radiation_s", 0.0), rep.get("time_total_s", 0.0)))
    A("=" * 68)
    return "\n".join(L)
