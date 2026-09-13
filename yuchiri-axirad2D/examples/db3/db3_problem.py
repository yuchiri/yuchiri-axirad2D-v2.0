# -*- coding: utf-8 -*-
"""DB-3 — mesh generation for the layered-skin benchmark.
DB-3 — 다층 피부 벤치마크의 격자 생성.

Properties and geometry live in db3_properties.py. This module only builds meshes,
which needs the solver.  물성과 형상은 db3_properties.py 에 있다. 이 모듈은 격자만
만들며, 그 일에는 솔버가 필요하다.

(original header follows / 원래 머리말)
DB-3 — layered skin with perfusion and radiative surface loss.
DB-3 — 관류가 있는 다층 피부와 복사 표면 손실.

Problem definition, mesh generation and comparison with the exact solution.
문제 정의, 격자 생성, 정확해 대조.

PROPERTY PROVENANCE / 물성 계보
================================
Values marked [LIT] are taken from the literature with the source recorded.
Values marked [SCENARIO] are chosen by this benchmark, with the reason recorded.

[LIT] 로 표시한 값은 문헌에서 가져오고 출처를 기록한다.
[SCENARIO] 로 표시한 값은 본 벤치마크가 정하며 그 이유를 기록한다.

The distinction is not "found" versus "not found".  It is a distinction of
KIND: emissivity, convection coefficient and ambient temperature describe the
SITUATION, not the tissue.  A benchmark author is entitled to set them; a
benchmark author is not entitled to invent tissue properties.
이 구분은 '찾았다/못 찾았다'가 아니라 '종류'의 구분이다.  방사율, 대류계수,
환경 온도는 조직이 아니라 '상황'을 기술한다.  벤치마크 작성자가 정할 수 있는
것은 상황이지 조직 물성이 아니다.

★ Literature values for skin differ substantially between research fields.
  The values below are ONE consistent set, not "the" values.  This benchmark
  verifies that a code solves the stated equations; it does not claim that the
  resulting temperatures are those of real skin.
★ 피부 물성값은 연구 분야마다 상당히 다르다.  아래는 정합적인 '하나의' 조합일
  뿐 '그' 값이 아니다.  본 벤치마크는 코드가 명시된 방정식을 맞게 푸는지를
  검증하며, 계산된 온도가 실제 피부의 온도라고 주장하지 않는다.
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

from gridgen import structured_quad9                       # noqa: E402
from axirad2d.mesh import Mesh, save_npz                   # noqa: E402

# Properties and geometry come from db3_properties.py, which is the single
# definition and is byte-identical to the copy in the benchmark suite.
# A test asserts that the two copies do not drift apart.
# 물성과 형상은 db3_properties.py 한 곳에서 온다. 벤치마크 모음의 사본과 바이트
# 단위로 같으며, 두 사본이 어긋나지 않는지 시험이 확인한다.
# Re-exported so that `import db3_problem as P` still sees the whole problem.
# `import db3_problem as P` 로 문제 전체가 보이도록 다시 내보낸다.
import db3_properties as _P                                  # noqa: E402
globals().update({k: v for k, v in vars(_P).items()
                  if not k.startswith("_")})
LAYERS, RHO_CB, Q_MET = _P.LAYERS, _P.RHO_CB, _P.Q_MET
T_ARTERIAL, L_SUB, L_DER = _P.T_ARTERIAL, _P.L_SUB, _P.L_DER
L_EPI, L_TOT, R_CYL, kappa = _P.L_EPI, _P.L_TOT, _P.R_CYL, _P.kappa
EPS_SKIN, H_CONV, T_INF = _P.EPS_SKIN, _P.H_CONV, _P.T_INF

# ======================================================================
# Mesh  /  격자
# ======================================================================
def build(refine=1, nr=3, perfusion_scale=1.0):
    """Cylinder of radius R_CYL, thickness L_TOT, layered along z.

    refine = 1, 2, 4  gives the h, h/2, h/4 sequence required by the
    order-of-convergence acceptance criterion.
    """
    zedges = [0.0, L_SUB, L_SUB + L_DER, L_TOT]
    # element counts per layer at refine = 1, chosen so the element size is
    # roughly uniform across layers rather than uniform in count
    base = [12, 4, 1]
    nz = [max(1, n * refine) for n in base]

    def mat(r, z):
        if z < L_SUB:
            return "subcutaneous"
        if z < L_SUB + L_DER:
            return "dermis"
        return "epidermis"

    g = structured_quad9([0.0, R_CYL], zedges, [nr * refine], nz, mat)
    nd = g["nodes"]
    tol = 1e-12 * L_TOT
    core = np.where(np.abs(nd[:, 1]) < tol)[0]
    surf = np.where(np.abs(nd[:, 1] - L_TOT) < tol)[0]
    return Mesh(nd, g["elems"], g["emat"], g["qvol"],
                {"core": core, "surface": surf})


def characteristic_h(refine):
    """Element size in the thinnest layer — the limiting length scale."""
    return L_EPI / max(1, 1 * refine)


if __name__ == "__main__":
    print("DB-3  layer stack (core -> surface) / 층 구성 (심부 -> 표면)")
    for nm, L, k, w in LAYERS:
        print("  %-13s L = %7.4f mm   k = %.3f   w = %.4f 1/s   kappa*L = %.4f"
              % (nm, L * 1e3, k, w, kappa(k, w) * L))
    print("  total thickness %.3f mm" % (L_TOT * 1e3))
    print("  rho_b c_b = %.6g J/(m^3 K)   T_a = %.2f K   q_met = %.1f W/m^3"
          % (RHO_CB, T_ARTERIAL, Q_MET))
    print("  eps = %.2f   h = %.1f W/(m^2 K)   T_inf = T_env = %.2f K"
          % (EPS_SKIN, H_CONV, T_INF))
    for rf in (1, 2, 4):
        m = build(rf)
        rep = {}
        m.check(report=rep)
        p = os.path.join(HERE, "db3_r%d.mesh.npz" % rf)
        save_npz(p, m)
        print("  refine %d : 절점 %5d  요소 %4d  h_min %.4f mm  G4 %.1e  지문 %s"
              % (rf, m.nn, m.ne, characteristic_h(rf) * 1e3,
                 rep["G4_rel_diff"], m.fingerprint()))
