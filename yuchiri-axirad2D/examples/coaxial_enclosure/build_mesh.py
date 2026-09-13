# -*- coding: utf-8 -*-
"""BM — 동축 원통 밀폐공동 (볼록 내부물체 완전 포위) 격자 생성.

  z=0.20 +-----------------------+
         |        shell          |
  z=0.18 +-------------------+   |
         |     vacuum        | s |
  z=0.15 +-----------+       | h |
         |   inner   |       | e |
  z=0.05 +-----------+       | l |
         |     vacuum        | l |
  z=0.02 +-------------------+   |
         |        shell          |
  z=0.00 +-----------------------+
       r=0        0.05   0.10  0.12

내부물체가 볼록하고 공동에 완전히 포위되므로 F(1->2) = 1, F(1->1) = 0 이다.
이 성질 덕분에 형상계수를 수치적분하지 않고도 정확해가 알려져 있다.
"""
from __future__ import annotations
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "src"))

from gridgen import structured_quad9                       # noqa: E402
from axirad2d.mesh import Mesh, save_npz                     # noqa: E402

# --- 형상 [m] ---------------------------------------------------------
A_IN, Z_IN0, Z_IN1 = 0.05, 0.05, 0.15          # 내부 원통
B_CAV, Z_CA0, Z_CA1 = 0.10, 0.02, 0.18         # 공동
C_OUT, Z_LO, Z_HI = 0.12, 0.00, 0.20           # 외곽

REDGES = [0.0, A_IN, B_CAV, C_OUT]
ZEDGES = [Z_LO, Z_CA0, Z_IN0, Z_IN1, Z_CA1, Z_HI]

# 내부물체 총 전력 [W] — 요소별 q_vol 로 환산해 넣는다 (§7)
P_TOTAL = 200.0
V_IN = np.pi * A_IN ** 2 * (Z_IN1 - Z_IN0)
QVOL = P_TOTAL / V_IN


def material_of(r, z):
    if r < A_IN and Z_IN0 < z < Z_IN1:
        return "inner_solid"
    if r < B_CAV and Z_CA0 < z < Z_CA1:
        return "cavity_vacuum"
    return "shell_solid"


def qvol_of(r, z, m):
    return QVOL if m == "inner_solid" else 0.0


def build(nr=(5, 5, 2), nz=(2, 3, 10, 3, 2)):
    g = structured_quad9(REDGES, ZEDGES, list(nr), list(nz),
                         material_of, qvol_of)
    nodes = g["nodes"]
    tol = 1e-12
    outer = np.where((np.abs(nodes[:, 0] - C_OUT) < tol)
                     | (np.abs(nodes[:, 1] - Z_LO) < tol)
                     | (np.abs(nodes[:, 1] - Z_HI) < tol))[0]
    nsets = {"outer_wall": outer}
    return Mesh(nodes, g["elems"], g["emat"], g["qvol"], nsets)


if __name__ == "__main__":
    m = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "coaxial_enclosure.mesh.npz")
    save_npz(out, m)
    print("절점 %d  요소 %d" % (m.nn, m.ne))
    print("q_vol = %.6g W/m^3   (총 %.6g W)" % (QVOL, P_TOTAL))
    print("지문 %s" % m.fingerprint())
    print("저장 ->", out)
