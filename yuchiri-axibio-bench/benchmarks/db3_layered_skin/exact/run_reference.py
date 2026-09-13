# -*- coding: utf-8 -*-
"""DB-3 — regenerate the reference values and check them.
DB-3 — 참조값을 다시 만들고 스스로 검사한다.

STANDALONE. Depends on numpy only. It does not import, and does not need, any
solver. That is the point of the suite: the reference must not come from the
thing it is grading.

독립 실행. numpy 에만 의존한다. 어떤 솔버도 부르지 않고 필요로 하지 않는다.
그것이 이 모음의 요점이다 — 참조값이 채점 대상에서 나오면 안 된다.

    python3 run_reference.py                 # print and rewrite reference_values.json
    python3 run_reference.py --check-only    # print only, write nothing
"""
from __future__ import annotations
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import db3_properties as P                                  # noqa: E402
from db3_exact import Layer, Stack, total_surface_loss      # noqa: E402

CASES = (("weak", 0.1), ("nominal", 1.0), ("strong", 10.0))


def stack(perfusion_scale=1.0):
    return Stack([Layer(n, L, k, w * perfusion_scale, P.Q_MET)
                  for n, L, k, w in P.LAYERS],
                 rho_cb=P.RHO_CB, T_a=P.T_ARTERIAL)


def solve(perfusion_scale=1.0):
    return stack(perfusion_scale).solve(
        T_core=P.T_CORE, h=P.H_CONV, T_inf=P.T_INF,
        eps=P.EPS_SKIN, T_env=P.T_ENV)


# ----------------------------------------------------------------------
def self_checks(verbose=True):
    """Four independently known limits the reference must reproduce.

    The reference is derived in this repository rather than cited, so it is
    checked against limits that are known without it.
    참조해를 인용이 아니라 여기서 유도했으므로, 참조해 없이도 알려진 극한
    네 가지로 검사한다.
    """
    out = []

    # 1) no perfusion, no radiation -> series resistance L/k + 1/h
    st = Stack([Layer("a", 0.002, 0.3, 0.0, 0.0)], rho_cb=3.77e6, T_a=310.15)
    r = st.solve(310.15, 10.0, 300.0, 0.0, 300.0)
    q = total_surface_loss(r["T_surface"], 10.0, 300.0, 0.0, 300.0)
    q_ex = (310.15 - 300.0) / (0.002 / 0.3 + 1.0 / 10.0)
    out.append(("series resistance / 직렬 저항", abs(q - q_ex), 1e-10))

    # 2) perfusion, adiabatic surface -> T == T_a everywhere
    st = Stack([Layer("a", 0.01, 0.5, 0.001, 0.0)], rho_cb=3.77e6, T_a=310.15)
    r = st.solve(310.15, 0.0, 300.0, 0.0, 300.0)
    d = float(np.abs(r["T_of_x"](np.linspace(0, 0.01, 9)) - 310.15).max())
    out.append(("adiabatic surface -> T = T_a / 단열 표면", d, 1e-10))

    # 3) perfusion balanced by metabolism -> uniform T_a + q/(w rho c)
    w, qm = 0.002, 500.0
    tp = qm / (w * 3.77e6)
    st = Stack([Layer("a", 0.02, 0.4, w, qm)], rho_cb=3.77e6, T_a=310.15)
    r = st.solve(310.15 + tp, 0.0, 300.0, 0.0, 300.0)
    d = float(np.abs(r["T_of_x"](np.linspace(0, 0.02, 9)) - (310.15 + tp)).max())
    out.append(("metabolic equilibrium / 대사 평형", d, 1e-10))

    # 4) splitting a layer in two must change nothing
    A = Stack([Layer("a", 0.004, 0.35, 0.001, 400.0)], 3.77e6, 310.15)
    B = Stack([Layer("a1", 0.001, 0.35, 0.001, 400.0),
               Layer("a2", 0.003, 0.35, 0.001, 400.0)], 3.77e6, 310.15)
    d = abs(A.solve(310.15, 8.0, 297.0, 0.98, 297.0)["T_surface"]
            - B.solve(310.15, 8.0, 297.0, 0.98, 297.0)["T_surface"])
    out.append(("layer splitting invariance / 층 쪼개기 불변", d, 1e-12))

    ok = True
    if verbose:
        print("Self-checks on the reference itself / 참조해 자체 검사")
    for name, val, tol in out:
        good = val <= tol
        ok &= good
        if verbose:
            print("  %-40s %.3e  (tol %.0e)  %s"
                  % (name, val, tol, "OK" if good else "FAIL"))
    return ok


# ----------------------------------------------------------------------
def build_reference():
    doc = {"benchmark_id": "DB-3", "suite_version": "0.2.0",
           "governing": "steady Pennes bioheat, layered, convective + "
                        "radiative surface loss",
           "note": "Verification reference, not a claim about real skin. "
                   "See problem.md section 7.",
           "properties": {
               "layers": [{"name": n, "L_m": L, "k_W_mK": k,
                           "perfusion_1_s": w, "q_met_W_m3": P.Q_MET,
                           "kappa_L": float(P.kappa(k, w) * L)}
                          for n, L, k, w in P.LAYERS],
               "rho_b_cb_J_m3K": P.RHO_CB, "T_arterial_K": P.T_ARTERIAL,
               "T_core_K": P.T_CORE, "emissivity": P.EPS_SKIN,
               "h_conv_W_m2K": P.H_CONV, "T_inf_K": P.T_INF,
               "T_env_K": P.T_ENV, "cylinder_radius_m": P.R_CYL},
           "cases": {}}
    for tag, sc in CASES:
        r = solve(sc)
        x = np.linspace(0.0, P.L_TOT, 25)
        doc["cases"][tag] = {
            "perfusion_scale": sc,
            "dimensionless_groups": {nm: float(kl)
                                     for nm, kl in P.dimensionless(sc)},
            "T_surface_K": float(r["T_surface"]),
            "surface_loss_W_m2": float(total_surface_loss(
                r["T_surface"], P.H_CONV, P.T_INF, P.EPS_SKIN, P.T_ENV)),
            "newton_residual": float(abs(r["residual"])),
            "profile_x_m": x.tolist(),
            "profile_T_K": r["T_of_x"](x).tolist()}
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description="DB-3 reference values")
    ap.add_argument("--check-only", action="store_true",
                    help="print only; do not write reference_values.json")
    a = ap.parse_args(argv)

    print(P.summary())
    print()
    ok = self_checks()
    print()
    doc = build_reference()
    print("Reference values / 참조값")
    print("  case      perfusion   T_surface [K]    surface loss [W/m^2]   "
          "Newton residual")
    for tag, _ in CASES:
        c = doc["cases"][tag]
        print("  %-9s x%-6.3g  %14.10f   %14.4f        %.1e"
              % (tag, c["perfusion_scale"], c["T_surface_K"],
                 c["surface_loss_W_m2"], c["newton_residual"]))
    if not a.check_only:
        out = os.path.join(os.path.dirname(HERE), "reference_values.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
        print("\nwritten / 기록: %s" % out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
