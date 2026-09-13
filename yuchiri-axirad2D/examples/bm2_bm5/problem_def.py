# -*- coding: utf-8 -*-
"""BM-2 and BM-5: geometry constants and exact-solution functions.
BM-2 · BM-5 의 형상 상수와 정확해 함수.

Not part of the solver. The figures are drawn by examples/plot_benchmark_definitions.py.
솔버의 일부가 아니다. 도면은 examples/plot_benchmark_definitions.py 가 그린다.
"""
from __future__ import annotations
import numpy as np

SIGMA = 5.670374419e-08

# ======================================================================
# BM-2  유한 원통 밀폐공동  (원판 - 측벽 - 원판)
# ======================================================================
BM2 = dict(
    R=0.05,          # 공동 반경 [m]
    L=0.10,          # 공동 길이 [m]
    T=0.02,          # 껍질 두께 [m]
    eps=1.0,         # 전 면 흑체  ->  B = F
    P=150.0,         # 아래 껍질에 넣는 총 발열 [W]
    T_out=300.0,     # 외곽 Dirichlet [K]
)


def bm2_view_factors(r1, r2, L):
    """동축 평행 원판의 형상계수 — 정확한 닫힌 형태.

        R1 = r1/L,  R2 = r2/L,  S = 1 + (1+R2^2)/R1^2
        F12 = 0.5 * { S - sqrt(S^2 - 4 (r2/r1)^2) }

    공개된 표준 수식이다. 어떤 수치표도 인용하지 않는다.
    """
    R1, R2 = r1 / L, r2 / L
    S = 1.0 + (1.0 + R2 * R2) / (R1 * R1)
    F12 = 0.5 * (S - np.sqrt(S * S - 4.0 * (r2 / r1) ** 2))
    A1 = np.pi * r1 ** 2
    As = 2.0 * np.pi * r1 * L                 # r1 = r2 인 경우의 측벽
    F1s = 1.0 - F12
    Fs1 = A1 * F1s / As
    Fss = 1.0 - 2.0 * Fs1
    return dict(F_disk_disk=F12, F_disk_side=F1s,
                F_side_disk=Fs1, F_side_side=Fss,
                A_disk=A1, A_side=As)


# ======================================================================
# BM-5  동심 구
# ======================================================================
BM5 = dict(
    a0=0.02,         # 내부 껍질 안쪽 반경 (격자 하한, 축 특이점 회피)
    a=0.04,          # 내부 구 표면 (복사면 1)
    b=0.08,          # 공동 바깥 표면 (복사면 2)
    c=0.10,          # 외곽 표면 (Dirichlet)
    eps1=0.8,
    eps2=0.5,
    P=300.0,
    T_out=300.0,
)


def bm5_exchange(T1, T2, a=None, b=None, e1=None, e2=None):
    """동심 구의 2면 정확해.

        Q = sigma (T1^4 - T2^4) / [ 1/(e1 A1) + (1/e2 - 1)/A2 ]

    ★ 이 식이 동심 구에서 정확한 이유 — 회전 대칭성 때문에 바깥 구 내면의
      조사량이 균일하다. 따라서 '각 면의 복사도가 균일'이라는 가정이
      실제로 성립한다.  (BM-1 의 원통 공동에서는 성립하지 않았다.)
    """
    a = BM5["a"] if a is None else a
    b = BM5["b"] if b is None else b
    e1 = BM5["eps1"] if e1 is None else e1
    e2 = BM5["eps2"] if e2 is None else e2
    A1 = 4.0 * np.pi * a * a
    A2 = 4.0 * np.pi * b * b
    R = 1.0 / (e1 * A1) + (1.0 / e2 - 1.0) / A2
    return SIGMA * (T1 ** 4 - T2 ** 4) / R, R, A1, A2


def bm5_exchange_areas(T1, T2, A1, A2, e1=None, e2=None):
    """면적을 직접 주는 형태 (다면체 근사 면적으로 대조할 때)."""
    e1 = BM5["eps1"] if e1 is None else e1
    e2 = BM5["eps2"] if e2 is None else e2
    R = 1.0 / (e1 * A1) + (1.0 / e2 - 1.0) / A2
    return SIGMA * (T1 ** 4 - T2 ** 4) / R


if __name__ == "__main__":
    vf = bm2_view_factors(BM2["R"], BM2["R"], BM2["L"])
    print("BM-2 형상계수 정확해 / exact view factors")
    for k, v in vf.items():
        print("   %-14s %.10f" % (k, v))
    Q, Rres, A1, A2 = bm5_exchange(1000.0, 300.0)
    print("BM-5  A1=%.10f  A2=%.10f  R=%.6f  Q(1000K,300K)=%.4f W"
          % (A1, A2, Rres, Q))
