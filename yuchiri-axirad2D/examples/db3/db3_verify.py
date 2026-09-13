# -*- coding: utf-8 -*-
"""DB-3 verification / DB-3 검증.

Runs the solver on the h, h/2, h/4 sequence and compares with the exact
solution, reporting the observed order of convergence.
h, h/2, h/4 계열로 풀어 정확해와 대조하고 관측 수렴 차수를 보고한다.

Acceptance is by ORDER OF CONVERGENCE, not by a fixed tolerance — a fixed
tolerance would be an unjustified constant (suite spec section 4).
합격 판정은 고정 허용오차가 아니라 수렴 차수로 한다.  고정 허용오차는 근거
없는 상수이기 때문이다 (yuchiri-axibio-bench SPEC.md 4장).
"""
from __future__ import annotations
import os
import sys
import numpy as np
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "examples"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from axirad2d.materials import Material, Poly              # noqa: E402
from axirad2d.assemble import Assembler                    # noqa: E402
import db3_problem as P                                    # noqa: E402
from db3_exact import Layer, Stack, total_surface_loss     # noqa: E402


def materials(perfusion_scale=1.0):
    out = {}
    for nm, L, k, w in P.LAYERS:
        out[nm] = Material(nm, Poly([k]), opaque=True, emissivity=P.EPS_SKIN,
                           perfusion=w * perfusion_scale, q_met=P.Q_MET)
    return out


def bcs():
    return [dict(type="dirichlet", nset="core", T=P.T_CORE),
            dict(type="convection", nset="surface",
                 h=P.H_CONV, T_inf=P.T_INF),
            dict(type="env_radiation", nset="surface",
                 emissivity=P.EPS_SKIN, T_env=P.T_ENV)]


def exact(perfusion_scale=1.0):
    st = Stack([Layer(nm, L, k, w * perfusion_scale, P.Q_MET)
                for nm, L, k, w in P.LAYERS],
               rho_cb=P.RHO_CB, T_a=P.T_ARTERIAL)
    return st, st.solve(T_core=P.T_CORE, h=P.H_CONV, T_inf=P.T_INF,
                        eps=P.EPS_SKIN, T_env=P.T_ENV)


def run(refine, perfusion_scale=1.0, itmax=40):
    m = P.build(refine)
    m.check()
    mats = materials(perfusion_scale)
    blood = dict(rho_cb=P.RHO_CB, T_arterial=P.T_ARTERIAL)
    A = Assembler(m, mats, bcs(), None, None, blood=blood)
    T = np.full(m.nn, P.T_CORE)
    T[A.dir_nodes] = A.dir_vals
    hist = []
    for _ in range(itmax):
        R, J, pw = A.residual_jacobian(T)
        Rd, Jd = A.apply_dirichlet(R, J, T)
        dT = spla.spsolve(Jd.tocsc(), -Rd)
        T = T + dT
        hist.append(float(np.abs(dT).max()))
        if hist[-1] < 1e-12:
            break
    R, J, pw = A.residual_jacobian(T)
    react = float(R[A.dir_nodes].sum())
    return m, T, pw, react, hist


def report(perfusion_scale=1.0, tag=""):
    st, ex = exact(perfusion_scale)
    print("=" * 78)
    print("DB-3  %s   (perfusion x %.3g)" % (tag, perfusion_scale))
    print("=" * 78)
    print("  kappa*L per layer :", ", ".join(
        "%s %.4f" % (nm, kL) for nm, kL in
        [(nm, (np.sqrt(w * perfusion_scale * P.RHO_CB / k) * L if w > 0 else 0.0))
         for nm, L, k, w in P.LAYERS]))
    print("  exact surface temperature  T_s = %.10f K" % ex["T_surface"])
    print("  exact surface loss         q  = %.10f W/m^2"
          % total_surface_loss(ex["T_surface"], P.H_CONV, P.T_INF,
                               P.EPS_SKIN, P.T_ENV))
    print("  reference Newton residual  %.2e   (machine precision)"
          % abs(ex["residual"]))
    print("-" * 78)
    print(" refine   nodes  elems   h[mm]     Linf err[K]     ratio   order p"
          "    r-var[K]")
    prev = None
    rows = []
    for rf in (1, 2, 4):
        m, T, pw, react, hist = run(rf, perfusion_scale)
        Tex = ex["T_of_x"](m.nodes[:, 1])
        e = float(np.abs(T - Tex).max())
        # radial variation: the exact solution has none, so any is a defect
        zs = np.unique(np.round(m.nodes[:, 1], 12))
        rvar = 0.0
        for z in zs:
            sel = np.abs(m.nodes[:, 1] - z) < 1e-14
            if sel.sum() > 1:
                rvar = max(rvar, float(T[sel].max() - T[sel].min()))
        ratio = "   -  " if prev is None else "%6.2f" % (prev / e)
        order = "   -  " if prev is None else "%6.2f" % np.log2(prev / e)
        print(" %5d %7d %6d  %7.4f   %.6e   %s   %s   %.2e"
              % (rf, m.nn, m.ne, P.characteristic_h(rf) * 1e3, e,
                 ratio, order, rvar))
        rows.append(dict(refine=rf, err=e, rvar=rvar, power=pw, react=react,
                         iters=len(hist), T=T, mesh=m))
        prev = e
    last = rows[-1]
    Pin = last["power"]["source"] + sum(
        v for k, v in last["power"].items()
        if k not in ("source", "radiation_net"))
    print("-" * 78)
    print("  energy balance :  in %.9g W   Dirichlet reaction %.9g W   "
          "relative residual %.2e"
          % (Pin, last["react"], abs(Pin + last["react"]) / max(abs(Pin), 1e-30)))
    print("  metabolic %.6g W   perfusion_net %.6g W"
          % (last["power"]["metabolic"], last["power"]["perfusion_net"]))
    print("  Newton iterations %d   max radial variation %.2e K  (exact: 0)"
          % (last["iters"], last["rvar"]))
    # computed surface temperature vs exact
    ms = last["mesh"]
    surf = np.abs(ms.nodes[:, 1] - P.L_TOT) < 1e-14
    print("  surface temperature  computed %.10f K   exact %.10f K   diff %.2e K"
          % (last["T"][surf].mean(), ex["T_surface"],
             last["T"][surf].mean() - ex["T_surface"]))
    return rows


if __name__ == "__main__":
    report(1.0, "nominal perfusion")
    print()
    report(0.1, "perfusion-weak  (conduction dominated)")
    print()
    report(10.0, "perfusion-strong (thin thermal layer)")
