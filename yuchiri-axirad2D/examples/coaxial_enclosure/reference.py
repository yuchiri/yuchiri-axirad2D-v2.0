# -*- coding: utf-8 -*-
"""BM 의 해석 참조값과 대조.

정확해의 근거
--------------
내부물체 1 이 볼록하고 공동 2 에 완전히 포위되므로

    F(1->1) = 0,   F(1->2) = 1                      (기하만으로 정확)

공동벽 2 를 흑체(e2 = 1)로 두면, 등온 상태에서 2 의 복사도는 sigma T2^4 로
균일하다. 1 이 볼록하므로 1 에서 반사된 광선은 반드시 2 로 간다. 따라서

    Q = e1 * A1 * sigma * (T1^4 - T2^4)                        (정확)

이 식에는 어떤 근사도 없다. 형상계수표를 인용할 필요도 없다.

★ 왜 e2 = 1 인가 — 회색벽(e2 < 1)의 2면 집중식

    Q = sigma (T1^4-T2^4) / [ (1-e1)/(e1 A1) + 1/(A1 F12) + (1-e2)/(e2 A2) ]

은 "각 면의 복사도가 균일하다"를 추가로 가정한다. 공동벽은 부위마다 조사량이
다르므로 이 가정이 성립하지 않는다. 본 코드처럼 면을 세분하면 그 비균일성을
실제로 푸는데, 그 결과는 집중식과 체계적으로 다르다 (이 형상에서 약 1.6 %).
따라서 집중식은 정확해가 아니며, 검증 기준으로 쓰면 안 된다.
"""
from __future__ import annotations
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "src"))
sys.path.insert(0, os.path.dirname(HERE))

from axirad2d.materials import SIGMA                     # noqa: E402
from build_mesh import (A_IN, Z_IN0, Z_IN1, B_CAV,     # noqa: E402
                        Z_CA0, Z_CA1, P_TOTAL)

E1, E2 = 0.8, 1.0

A1 = 2.0 * np.pi * A_IN * (Z_IN1 - Z_IN0) + 2.0 * np.pi * A_IN ** 2
A2 = 2.0 * np.pi * B_CAV * (Z_CA1 - Z_CA0) + 2.0 * np.pi * B_CAV ** 2
RTOT = 1.0 / (E1 * A1)          # e2 = 1 에서 정확


def T1_exact(T2, Q=P_TOTAL):
    """정확해 — 볼록체 완전 포위 + 흑체 공동벽."""
    return (T2 ** 4 + Q * RTOT / SIGMA) ** 0.25


def Q_exact(T1, T2):
    """정확해 — Q = e1 A1 sigma (T1^4 - T2^4)."""
    return SIGMA * (T1 ** 4 - T2 ** 4) / RTOT


def Q_lumped(T1, T2, e2=0.6):
    """참고 — 회색벽 2면 집중식. 정확해가 아니다."""
    R = (1 - E1) / (E1 * A1) + 1.0 / A1 + (1 - e2) / (e2 * A2)
    return SIGMA * (T1 ** 4 - T2 ** 4) / R


def main():
    out = os.path.join(HERE, "out", "results.npz")
    if not os.path.exists(out):
        print("먼저 계산을 실행하라:  python -m axirad2d.cli case.toml")
        return 1
    z = np.load(out)
    P1, P2, area, Ts = z["seg_P1"], z["seg_P2"], z["seg_area"], z["seg_T"]
    rmid = 0.5 * (P1[:, 0] + P2[:, 0])
    zmid = 0.5 * (P1[:, 1] + P2[:, 1])
    inner = (rmid <= A_IN + 1e-12) & (zmid >= Z_IN0 - 1e-12) & (zmid <= Z_IN1 + 1e-12)
    a1, a2 = area[inner].sum(), area[~inner].sum()
    # 면적 가중 4승 평균 (복사에서 의미 있는 평균)
    T1n = (np.sum(area[inner] * Ts[inner] ** 4) / a1) ** 0.25
    T2n = (np.sum(area[~inner] * Ts[~inner] ** 4) / a2) ** 0.25

    print("=" * 66)
    print("BM 해석 참조값 대조")
    print("=" * 66)
    print("면적   A1 계산 %.10f  해석 %.10f  차 %.2e" % (a1, A1, abs(a1 - A1)))
    print("       A2 계산 %.10f  해석 %.10f  차 %.2e" % (a2, A2, abs(a2 - A2)))
    print("-" * 66)
    print("표면온도 (면적가중 4승평균)")
    print("       내부물체 T1 = %.4f K" % T1n)
    print("       공동벽   T2 = %.4f K" % T2n)
    print("-" * 66)
    print("해석해 대조")
    print("       T1(해석, T2=%.4f) = %.4f K   차 %+.4f K  (%.4f %%)"
          % (T2n, T1_exact(T2n), T1n - T1_exact(T2n),
             100.0 * (T1n - T1_exact(T2n)) / T1_exact(T2n)))
    q = Q_exact(T1n, T2n)
    print("       Q(해석, 계산온도) = %.4f W   투입 %.4f W  차 %+.4f W  (%.4f %%)"
          % (q, P_TOTAL, q - P_TOTAL, 100.0 * (q - P_TOTAL) / P_TOTAL))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
