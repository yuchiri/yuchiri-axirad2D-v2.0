# -*- coding: utf-8 -*-
"""BM-2 · BM-5 결과를 정확해와 대조한다.

    python -m axirad2d.cli examples/bm2_bm5/case_bm2.toml -o examples/bm2_bm5/out_bm2
    python -m axirad2d.cli examples/bm2_bm5/case_bm5.toml -o examples/bm2_bm5/out_bm5
    python examples/bm2_bm5/verify.py
"""
from __future__ import annotations
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "examples"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from axirad2d.materials import Material, Poly, SIGMA          # noqa: E402
from axirad2d import surfaces, montecarlo                     # noqa: E402
from build_meshes import build_bm2, build_bm5               # noqa: E402
from problem_def import (BM2, BM5, bm2_view_factors,        # noqa: E402
                         bm5_exchange, bm5_exchange_areas)

LINE = "=" * 74


def group_F(S, B, g1, g2):
    return float(S.area[g1] @ B[np.ix_(g1, g2)].sum(axis=1) / S.area[g1].sum())


# ----------------------------------------------------------------------
def verify_bm2(n_ray=60000, seeds=(1, 2, 3, 4, 5, 6, 7, 8)):
    print(LINE)
    print("BM-2  유한 원통 밀폐공동 — 형상계수 정확해 대조")
    print(LINE)
    m = build_bm2()
    mats = {"shell": Material("shell", Poly([30.0]), True, 1.0),
            "vacuum": Material("vacuum", Poly([1e-5]), opaque=False)}
    rep = {}
    m.check(report=rep)
    S = surfaces.extract(m, mats, 1.0, rep)
    zm = 0.5 * (S.P1[:, 1] + S.P2[:, 1])
    rm = 0.5 * (S.P1[:, 0] + S.P2[:, 0])
    d1 = np.abs(zm) < 1e-9
    d2 = np.abs(zm - BM2["L"]) < 1e-9
    sd = np.abs(rm - BM2["R"]) < 1e-9
    ex = bm2_view_factors(BM2["R"], BM2["R"], BM2["L"])

    print("격자   절점 %d  요소 %d   G4 상대차 %.2e (허용 %.2e)"
          % (m.nn, m.ne, rep["G4_rel_diff"], rep["G4_tol"]))
    print("복사면 세그먼트 %d = 원판1 %d + 원판2 %d + 측벽 %d"
          % (len(S), d1.sum(), d2.sum(), sd.sum()))
    print("면적   A_원판 %.12f (정확 %.12f)  차 %.1e"
          % (S.area[d1].sum(), ex["A_disk"], abs(S.area[d1].sum() - ex["A_disk"])))
    print("       A_측벽 %.12f (정확 %.12f)  차 %.1e"
          % (S.area[sd].sum(), ex["A_side"], abs(S.area[sd].sum() - ex["A_side"])))
    print("-" * 74)
    print("전 면 흑체 (eps = 1)  ->  B = F.  씨앗 %d개, 광선 %d" % (len(seeds), n_ray))
    v12, vs1, v11 = [], [], []
    for s in seeds:
        r = {}
        B, _, _ = montecarlo.gebhart(S, n_ray=n_ray, seed=s, report=r)
        v12.append(group_F(S, B, d1, d2))
        vs1.append(group_F(S, B, sd, d1))
        v11.append(group_F(S, B, d1, d1))
    for name, arr, exact in (("F(원판1->원판2)", np.array(v12), ex["F_disk_disk"]),
                             ("F(측벽 ->원판1)", np.array(vs1), ex["F_side_disk"])):
        se = arr.std(ddof=1) / np.sqrt(len(arr))
        err = (arr.mean() - exact) / exact
        print("  %s  평균 %.9f  정확 %.9f  오차 %+.4f %%  "
              "(표준오차 %.4f %%, %.2f sigma)"
              % (name, arr.mean(), exact, 100 * err, 100 * se / exact,
                 abs(arr.mean() - exact) / max(se, 1e-300)))
    print("  F(원판1->원판1)  최대 %.3e   (정확 0)" % max(v11))
    print("  폐쇄성 %.12f   누출 %.1e" % (r["closure_min"], r["leak_open"]))
    return ex


# ----------------------------------------------------------------------
def verify_bm5(n_ray=40000, seeds=(21,)):
    print()
    print(LINE)
    print("BM-5  동심 구 — 회색벽 2면 정확해 대조")
    print(LINE)
    a, b = BM5["a"], BM5["b"]
    e1, e2 = BM5["eps1"], BM5["eps2"]

    # --- (1) 곡면 근사 수렴 -----------------------------------------
    print("곡면 근사 수렴 (원뿔대가 구면을 근사)")
    print("  nth  세그먼트   A1 오차 %      비")
    prev = None
    for nth in (12, 24, 48):
        mm = build_bm5(ntheta=(nth,))
        SS = surfaces.extract(mm, _mats(1.0, 1.0), 1.0, {})
        rho = np.hypot(0.5 * (SS.P1[:, 0] + SS.P2[:, 0]),
                       0.5 * (SS.P1[:, 1] + SS.P2[:, 1]))
        A1 = SS.area[rho < 0.5 * (a + b)].sum()
        e = (A1 - 4 * np.pi * a * a) / (4 * np.pi * a * a)
        print("  %-4d %-10d %+8.4f    %s" % (nth, len(SS), 100 * e,
                                             "-" if prev is None else "%.2f" % (prev / e)))
        prev = e
    print("  -> Delta_theta^2 수렴 (현이 원호를 근사할 때의 이론값)")

    # --- (2) 흑체 검사 -----------------------------------------------
    m = build_bm5()
    Sb = surfaces.extract(m, _mats(1.0, 1.0), 1.0, {})
    rho = np.hypot(0.5 * (Sb.P1[:, 0] + Sb.P2[:, 0]),
                   0.5 * (Sb.P1[:, 1] + Sb.P2[:, 1]))
    inn = rho < 0.5 * (a + b)
    rb = {}
    Bb, _, _ = montecarlo.gebhart(Sb, n_ray=20000, seed=7, report=rb)
    print("-" * 74)
    print("흑체 한계 (eps = 1)  ->  B = F")
    print("  F(1->1) = %.3e (정확 0)   F(1->2) = %.12f (정확 1)"
          % (group_F(Sb, Bb, inn, inn), group_F(Sb, Bb, inn, ~inn)))
    print("  ※ 회색이면 B(1->1) != 0 이다. 바깥 구에서 반사되어 돌아온 광선이 잡힌다.")

    # --- (3) 회색 정확해 ---------------------------------------------
    S = surfaces.extract(m, _mats(e1, e2), e2, {})
    A1, A2 = S.area[inn].sum(), S.area[~inn].sum()
    T1, T2 = 1000.0, 300.0
    print("-" * 74)
    print("회색 등온 2면 교환  (eps1 = %.1f, eps2 = %.1f, T1 = %.0f K, T2 = %.0f K)"
          % (e1, e2, T1, T2))
    for s in seeds:
        B, _, _ = montecarlo.gebhart(S, n_ray=n_ray, seed=s)
        w = SIGMA * S.area * S.eps
        M = (B * w[:, None]).T
        T4 = np.where(inn, T1, T2) ** 4
        Qc = -(M @ T4 - w * T4)[inn].sum()
        Qa = bm5_exchange_areas(T1, T2, A1, A2)
        Qs, _, _, _ = bm5_exchange(T1, T2)
        print("  Q_code      = %.4f W" % Qc)
        print("  Q_정확(계산 면적)  = %.4f W   오차 %+.4f %%" % (Qa, 100 * (Qc - Qa) / Qa))
        print("  Q_정확(참 구면)    = %.4f W   오차 %+.4f %%   <- 면적 이산화 포함"
              % (Qs, 100 * (Qc - Qs) / Qs))
    print()
    print("  ★ BM-1(원통 공동)에서는 같은 집중식이 -1.6 %% 어긋났고 광선을 늘려도")
    print("    줄지 않았다. 동심 구에서는 회전 대칭성 때문에 조사량이 균일하여")
    print("    집중식이 정확해진다. 위 결과가 그 설명을 뒷받침한다.")


def _mats(e1, e2):
    return {"inner_solid": Material("inner_solid", Poly([400.0]), True, e1),
            "outer_solid": Material("outer_solid", Poly([400.0]), True, e2),
            "vacuum": Material("vacuum", Poly([1e-5]), opaque=False)}


# ----------------------------------------------------------------------
def verify_coupled():
    print()
    print(LINE)
    print("결합 해석 결과 (cli 실행 결과가 있을 때)")
    print(LINE)
    for tag, p in (("BM-2", "out_bm2"), ("BM-5", "out_bm5")):
        f = os.path.join(HERE, p, "results.npz")
        if not os.path.exists(f):
            print("  %s : 결과 없음 (cli 를 먼저 실행하라)" % tag)
            continue
        z = np.load(f)
        T = z["T"]
        print("  %s : 절점 온도 [%.2f, %.2f] K" % (tag, T.min(), T.max()))
        if tag == "BM-5":
            Ts, area = z["seg_T"], z["seg_area"]
            rho = np.hypot(0.5 * (z["seg_P1"][:, 0] + z["seg_P2"][:, 0]),
                           0.5 * (z["seg_P1"][:, 1] + z["seg_P2"][:, 1]))
            inn = rho < 0.5 * (BM5["a"] + BM5["b"])
            A1, A2 = area[inn].sum(), area[~inn].sum()
            T1 = (np.sum(area[inn] * Ts[inn] ** 4) / A1) ** 0.25
            T2 = (np.sum(area[~inn] * Ts[~inn] ** 4) / A2) ** 0.25
            Q = bm5_exchange_areas(T1, T2, A1, A2)
            print("        표면온도 T1 = %.4f K,  T2 = %.4f K" % (T1, T2))
            print("        Q(정확해, 계산 온도·면적) = %.4f W   투입 %.1f W   "
                  "오차 %+.4f %%" % (Q, BM5["P"], 100 * (Q - BM5["P"]) / BM5["P"]))


if __name__ == "__main__":
    verify_bm2()
    verify_bm5()
    verify_coupled()
