# -*- coding: utf-8 -*-
"""BM-2 · BM-5 격자 생성.

★ 솔버의 일부가 아니다. 외부 메셔 역할을 하는 보조 스크립트다 (README).
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

from gridgen import structured_quad9, structured_quad9_mapped   # noqa: E402
from axirad2d.mesh import Mesh, save_npz                          # noqa: E402
from problem_def import BM2, BM5                                # noqa: E402


# ======================================================================
# BM-2
# ======================================================================
def build_bm2(nr=(5, 2), nz=(2, 10, 2)):
    R, L, t = BM2["R"], BM2["L"], BM2["T"]
    V_bot = np.pi * (R + t) ** 2 * t
    q = BM2["P"] / V_bot

    def mat(r, z):
        return "vacuum" if (r < R and 0.0 < z < L) else "shell"

    def qv(r, z, m):
        return q if (m == "shell" and z < 0.0) else 0.0

    g = structured_quad9([0.0, R, R + t], [-t, 0.0, L, L + t],
                         list(nr), list(nz), mat, qv)
    nd = g["nodes"]
    tol = 1e-12
    outer = np.where((np.abs(nd[:, 0] - (R + t)) < tol)
                     | (np.abs(nd[:, 1] + t) < tol)
                     | (np.abs(nd[:, 1] - (L + t)) < tol))[0]
    return Mesh(nd, g["elems"], g["emat"], g["qvol"], {"outer_wall": outer})


# ======================================================================
# BM-5   (rho, theta) -> (r, z) = (rho sin th, rho cos th)
# ======================================================================
def build_bm5(nrho=(2, 4, 2), ntheta=(24,)):
    a0, a, b, c = BM5["a0"], BM5["a"], BM5["b"], BM5["c"]
    V_in = 4.0 / 3.0 * np.pi * (a ** 3 - a0 ** 3)
    q = BM5["P"] / V_in

    def mp(rho, th):
        r = rho * np.sin(th)
        if abs(r) < 1e-14 * max(rho, 1e-300):      # 축 스냅 (sin(pi) != 0)
            r = 0.0
        return (r, rho * np.cos(th))

    def mat(rho, th):
        if rho < a:
            return "inner_solid"
        if rho < b:
            return "vacuum"
        return "outer_solid"

    def qv(rho, th, m):
        return q if m == "inner_solid" else 0.0

    g = structured_quad9_mapped([a0, a, b, c], [0.0, np.pi],
                                list(nrho), list(ntheta), mp, mat, qv)
    nd = g["nodes"]
    rr = np.hypot(nd[:, 0], nd[:, 1])
    outer = np.where(np.abs(rr - c) < 1e-9 * c)[0]
    return Mesh(nd, g["elems"], g["emat"], g["qvol"], {"outer_wall": outer})


if __name__ == "__main__":
    for name, m in (("bm2", build_bm2()), ("bm5", build_bm5())):
        p = os.path.join(HERE, "%s.mesh.npz" % name)
        save_npz(p, m)
        rep = {}
        m.check(report=rep)
        print("%s : 절점 %d  요소 %d   G4 상대차 %.2e (허용 %.2e)  지문 %s"
              % (name, m.nn, m.ne, rep["G4_rel_diff"], rep["G4_tol"],
                 m.fingerprint()))
