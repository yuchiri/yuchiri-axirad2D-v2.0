# -*- coding: utf-8 -*-
"""[EN] Material properties: functions of temperature only, isotropic,
given as polynomial coefficients.

Specification section 6.   f(T) = sum c_p T^p + sum d_n / T^n

[KO] 물성 — 온도만의 함수. 등방. 다항식 계수 형식.

See USER_GUIDE section 5 (materials).
공개 문서 USER_GUIDE 5장 참조.

    f(T) = sum_{p>=0} c_p T^p  +  sum_{n>=1} d_n / T^n
"""
from __future__ import annotations
import numpy as np

SIGMA = 5.670374419e-08          # W/(m^2 K^4)  §2.3


class MaterialError(Exception):
    pass


class Poly:
    """양·음의 거듭제곱을 함께 갖는 온도 다항식."""

    def __init__(self, pos=(), neg=None):
        self.pos = np.asarray(list(pos), dtype=float)
        self.neg = {int(k): float(v) for k, v in dict(neg or {}).items()}
        if any(k < 1 for k in self.neg):
            raise MaterialError("음의 거듭제곱 지수는 1 이상이어야 한다")

    def __call__(self, T):
        T = np.asarray(T, dtype=float)
        out = np.zeros_like(T)
        for p, c in enumerate(self.pos):
            if c:
                out = out + c * T ** p
        for n, d in self.neg.items():
            out = out + d / T ** n
        return out

    def d(self, T):
        """dF/dT — 해석적 미분 (§6.1)."""
        T = np.asarray(T, dtype=float)
        out = np.zeros_like(T)
        for p, c in enumerate(self.pos):
            if c and p >= 1:
                out = out + c * p * T ** (p - 1)
        for n, dd in self.neg.items():
            out = out - dd * n / T ** (n + 1)
        return out

    def is_zero(self):
        return not np.any(self.pos) and not self.neg


class Material:
    """[EN] Tissue / solid material.

    Perfusion and metabolic heat are properties of the TISSUE and live here.
    Blood heat capacity and arterial temperature are properties of BLOOD and
    live at problem level (see Assembler(blood=...)), because they are the same
    for every tissue in one body and duplicating them per material would let
    them disagree.

    [KO] 관류율과 대사 발열은 '조직'의 성질이므로 여기에 둔다.
    혈액의 체적 열용량과 동맥혈 온도는 '혈액'의 성질이므로 문제 수준에 둔다.
    한 개체 안에서는 모든 조직에 대해 같은 값이며, 재료마다 복제하면 서로
    어긋날 수 있기 때문이다.
    """

    def __init__(self, name, k, opaque=True, emissivity=None,
                 rho=None, cp=None, T_range=None,
                 perfusion=0.0, q_met=0.0):
        self.name = name
        self.k = k
        # 관류율 omega_b [1/s].  상수로 둔다 — 온도 의존 모델에 합의가 없고,
        # 의존시키면 야코비안에 d(omega)/dT 항이 생긴다 (미결).
        self.perfusion = float(perfusion)
        # 대사 발열 [W/m^3].  같은 이유로 상수.
        self.q_met = float(q_met)
        if self.perfusion < 0.0:
            raise MaterialError("재료 '%s' 의 관류율은 음수일 수 없다" % name)
        self.opaque = bool(opaque)
        self.emissivity = emissivity
        self.rho = rho
        self.cp = cp
        self.T_range = None if T_range is None else (float(T_range[0]), float(T_range[1]))
        if self.opaque and self.emissivity is None:
            raise MaterialError("불투명 재료 '%s' 에 방사율이 없다" % name)
        if self.opaque and not (0.0 < float(self.emissivity) <= 1.0):
            raise MaterialError("재료 '%s' 의 방사율은 (0, 1] 이어야 한다" % name)


def check_k_positive(name, kval):
    """§6.3 — 실제로 쓰인 k 가 0 이하이면 즉시 중단."""
    if np.any(np.asarray(kval) <= 0.0):
        raise MaterialError(
            "재료 '%s' 의 열전도도가 0 이하이다 (최소 %.6g). "
            "물성 계수 또는 유효 온도 범위를 확인하라." % (name, float(np.min(kval))))
