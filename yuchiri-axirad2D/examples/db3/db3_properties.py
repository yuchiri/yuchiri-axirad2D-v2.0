# -*- coding: utf-8 -*-
"""DB-3 — problem definition: geometry, properties and their provenance.
DB-3 — 문제 정의: 형상, 물성, 그리고 그 출처.

STANDALONE. Depends on numpy only. No solver, no mesh generation.
독립 실행. numpy 에만 의존한다. 솔버도 격자 생성도 필요 없다.

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
import numpy as np


# ======================================================================
# Tissue properties  /  조직 물성
# ======================================================================
# [LIT] Parvin et al., Engineering Reports (Wiley, 2025):
#       three-layer skin model with ke = 0.21, kd = 0.37, ks = 0.16 W/(m K)
K_EPI, K_DER, K_SUB = 0.21, 0.37, 0.16

# [LIT] The epidermis has no blood vessels, so its perfusion rate is zero.
#       (Electronics Cooling 2023; and the perfusion term is discarded for the
#        epidermis in skin bioheat models — ScienceDirect topic review)
W_EPI = 0.0

# [LIT] Blood perfusion rate is usually within 0 – 0.1 mL blood/mL tissue/s and
#       is taken as 0.038 in that work.  (Sci. Rep. 8, 2018)
W_DER = W_SUB = 0.038                     # [1/s]

# [LIT] Blood specific heat 3770 J/(kg K), density 1060 kg/m^3.  (Sci. Rep. 2018)
RHO_CB = 1060.0 * 3770.0                  # [J/(m^3 K)]  = 3.9962e6

# [LIT] Metabolic heat generation 368.1 W/m^3.  (Sci. Rep. 2018)
Q_MET = 368.1                             # [W/m^3]

# [LIT] Blood temperature and core body temperature are 37 degC.  (Sci. Rep. 2018)
T_CORE = T_ARTERIAL = 310.15              # [K]

# [LIT] thickness ratios: dermis is about 12x the epidermis on the inner
#       forearm, and the subcutaneous layer about 3x the dermis.
#       (Electronics Cooling 2023)
# [SCENARIO] absolute scale.  The ratios are from the literature; the absolute
#       thickness varies by body site, so one value must be chosen.  0.1 mm
#       epidermis gives a forearm-like stack of 4.9 mm in total.
L_EPI = 0.1e-3                            # [m]
L_DER = 12.0 * L_EPI                      # 1.2 mm
L_SUB = 3.0 * L_DER                       # 3.6 mm
L_TOT = L_EPI + L_DER + L_SUB             # 4.9 mm

# ======================================================================
# Situation  /  상황
# ======================================================================
# [LIT] Steketee, J. (1973), "Spectral emissivity of skin and pericardium":
#       a monochromator measurement over 1-14 micrometres found the emissivity of
#       skin to be independent of wavelength and equal to 0.98 +/- 0.01, and
#       independent of skin pigmentation.  Re-measured in 2009 by CO2-laser
#       reflection as 0.976 +/- 0.006, and agreed on by 96 % of experts in a
#       Delphi study.
#       CAVEAT: this holds in the long-wave infrared, which is where a body near
#       room temperature radiates.  In the mid-wave band (3-5 um) values of
#       0.91-0.92 have been proposed instead.
#       [KO] Steketee (1973) 가 1-14 um 에서 측정한 값으로, 파장에 무관하고
#       색소 침착에도 무관하게 0.98 +/- 0.01 이다.  2009년 CO2 레이저 반사법
#       재측정 0.976 +/- 0.006.  단서 — 상온 물체가 복사하는 장파 적외선에서
#       성립한다.  중파(3-5 um)에서는 0.91-0.92 가 제안된다.
EPS_SKIN = 0.98

# [SCENARIO, within the reported range] Indoor natural convection.
#       Whole-body natural-convection coefficients reported for the human body:
#           5.1  Colin & Houdas (1967)
#           4.9 / 4.3  Ichihara et al. (standing / seated)
#           4.0  Seppaenen et al. (1972)
#           3.4 / 3.3  de Dear et al. (1997), thermal manikin
#           3.3  Omori et al. (2004)
#           3.1  Mitchell (1974)
#       Per body segment the reported spread is 0.9-5.5 W/(m^2 K).
#       5.0 is therefore inside the reported range but at its HIGH end, above the
#       modern whole-body consensus of about 3.3-3.4.  It was chosen so that
#       convection and radiation come out COMPARABLE: the linearised radiative
#       coefficient here is 4 eps sigma T_m^3 = 6.20 W/(m^2 K).  Lowering h to
#       3.4 would push radiation to about 65 % and test the convective term less.
#       A benchmark coefficient has to be admissible and has to exercise the
#       terms under test; it does not have to be a best estimate of any person.
#       [KO] 인체 전신 자연대류 계수의 보고값은 위와 같고, 부위별로는
#       0.9-5.5 W/(m^2 K) 범위다.  5.0 은 보고 범위 안이지만 높은 쪽이며,
#       현대 전신 합의치 3.3-3.4 보다 크다.  대류와 복사가 비슷한 크기가 되도록
#       고른 값이다 — 여기서 선형화 복사계수가 4 eps sigma T_m^3 = 6.20 이다.
#       h 를 3.4 로 낮추면 복사가 65 % 가 되어 대류 항이 덜 시험된다.
#       벤치마크의 계수는 허용 가능해야 하고 시험 대상 항을 실제로 시험해야
#       한다.  누군가의 최선 추정치일 필요는 없다.
H_CONV = 5.0                              # [W/(m^2 K)]

# [SCENARIO] Room condition.  Ambient air and surrounding surfaces at the same
#       temperature, so a single number defines the environment.
T_INF = T_ENV = 297.15                    # [K]  (24 degC)

# ---------------------------------------------------------------------------
# [EN] ON THE LINEARISED RADIATIVE COEFFICIENT
#      Here 4 eps sigma T_m^3 = 6.20 W/(m^2 K) at T_m = 303.3 K, while the
#      measured WHOLE-BODY radiative coefficient is about 4.5-4.7 W/(m^2 K).
#      These do not contradict each other.  The whole-body figure carries an
#      effective-radiating-area factor of roughly 0.7, because limbs face one
#      another and not the room.  This benchmark poses a FLAT surface, for which
#      that factor is 1, so 6.20 is the right number for the geometry as stated.
# [KO] 선형화 복사계수에 관하여
#      여기서 4 eps sigma T_m^3 = 6.20 W/(m^2 K) 인데, 실측 '전신' 복사계수는
#      약 4.5-4.7 이다.  모순이 아니다.  전신값은 유효 복사 면적 인자(약 0.7)를
#      포함한다.  팔다리가 서로를 마주 보아 방을 향해 복사하지 못하기 때문이다.
#      이 벤치마크는 '평평한' 표면을 낸 것이므로 그 인자가 1 이고, 명시된 형상에
#      대해 6.20 이 맞는 값이다.
# ---------------------------------------------------------------------------
# [EN] WHY THESE COEFFICIENTS ARE DEFENSIBLE FOR A VERIFICATION BENCHMARK
#      A coefficient here has to satisfy three things, and being a best estimate
#      of real tissue is not one of them:
#        1. It must be FIXED AND PUBLISHED, because the exact solution is a
#           function of these numbers; if they drift, the reference is not
#           reproducible.
#        2. It must be PHYSICALLY ADMISSIBLE — right sign, right order, inside
#           the ranges the literature reports.
#        3. It must make the benchmark EXERCISE THE TERMS IT CLAIMS TO TEST.
#      The reference is an exact solution of the stated equations, not a
#      measurement.  Whatever coefficients are put in, the exact solution is
#      exact for them.  Realism of the coefficients therefore does not affect the
#      correctness of the reference — it affects validation, which this suite
#      explicitly does not claim.
#      For realistic, statistically documented tissue values, use the IT'IS
#      database instead: Baumgartner et al., "IT'IS Database for thermal and
#      electromagnetic parameters of biological tissues", Version 5.0,
#      2025-08-21, DOI 10.13099/VIP21000-05-0, itis.swiss/database.  That
#      database itself warns that for some parameters, perfusion in particular,
#      the spread is large enough to affect simulation results severely.
# [KO] 이 계수들이 검증 벤치마크로서 방어되는 이유
#      여기서 계수는 세 가지를 만족해야 하며, '실제 조직의 최선 추정치일 것' 은
#      그중에 없다.
#        1. 고정되고 공개될 것.  정확해가 이 값들의 함수이므로, 값이 흔들리면
#           참조값이 재현되지 않는다.
#        2. 물리적으로 허용될 것 — 부호, 자릿수, 문헌이 보고한 범위 안.
#        3. 시험하려는 항을 실제로 시험하게 할 것.
#      참조값은 측정이 아니라 명시된 방정식의 정확해다.  어떤 계수를 넣든 정확해는
#      그 계수에 대해 정확하다.  따라서 계수의 현실성은 참조값의 정확성과 무관하며,
#      그것이 좌우하는 것은 '확인' 이고 이 모음은 확인을 주장하지 않는다.
#      현실적이고 통계까지 문서화된 조직 물성이 필요하면 IT'IS 데이터베이스를
#      쓰라 (위 DOI).  그 데이터베이스 스스로, 일부 파라미터 특히 관류는 변동이
#      커서 시뮬레이션 결과에 심각한 영향을 줄 수 있다고 경고한다.
# ---------------------------------------------------------------------------
# [EN] WHAT LEAVES THE SURFACE, AND WHAT DOES NOT
#      The surface loses heat by convection and by radiation, and by nothing
#      else in this benchmark.  There is NO evaporative term: neither insensible
#      perspiration nor sweating is modelled, because that is mass transfer and
#      this is a heat-transfer benchmark.  Respiratory loss is outside a skin
#      balance altogether.
#      This is one reason the computed surface temperature, 36.30 degC, comes out
#      HIGHER than measured human skin, which sits near 32-34 degC in a 24 degC
#      room: an output term is missing, so the surface runs warm.  The thickness,
#      the property set and the choice of h also contribute; how much each one
#      contributes has not been computed and is not claimed here.
#
# [KO] 표면에서 무엇이 나가고 무엇이 나가지 않는가
#      이 벤치마크에서 표면은 대류와 복사로만 열을 잃는다.  증발 항이 **없다**.
#      무감성 발한도 땀도 모델링하지 않는다.  그것은 물질전달이고 이것은 열전달
#      벤치마크이기 때문이다.  호흡을 통한 손실은 애초에 피부 수지 밖이다.
#      계산된 표면 온도 36.30 degC 가 실측 인체 피부(24 degC 실내에서 32~34 degC)
#      보다 **높게** 나오는 이유 중 하나가 이것이다.  출력 항이 하나 빠지면 표면이
#      더워진다.  두께, 물성 조합, h 의 선택도 함께 작용하며, 각각이 얼마나
#      기여하는지는 계산하지 않았고 여기서 주장하지 않는다.
# ---------------------------------------------------------------------------

# [SCENARIO] Cylinder radius.  The lateral surface is adiabatic, so the exact
#       solution has NO r-dependence.  R is arbitrary; any radial variation in
#       the computed field is a defect signal, not physics.
#       측면이 단열이므로 정확해에 r 의존성이 없다.  R 은 임의이며, 계산된 장에
#       반경 변화가 나타나면 그것은 물리가 아니라 결함 신호다.
R_CYL = 5.0e-3                            # [m]

LAYERS = [("subcutaneous", L_SUB, K_SUB, W_SUB),   # core side  (x = 0)
          ("dermis",       L_DER, K_DER, W_DER),
          ("epidermis",    L_EPI, K_EPI, W_EPI)]   # surface    (x = L_TOT)


def kappa(k, w):
    """Perfusion wavenumber [1/m].  kappa = sqrt(w rho_b c_b / k)."""
    return np.sqrt(w * RHO_CB / k) if w > 0 else 0.0




def dimensionless(perfusion_scale=1.0):
    """kappa_i L_i per layer — the groups that govern the solution.

    층별 kappa_i L_i — 해를 지배하는 무차원 수.
    """
    return [(nm, kappa(k, w * perfusion_scale) * L) for nm, L, k, w in LAYERS]


def summary():
    lines = ["DB-3  layer stack (core -> surface) / 층 구성 (심부 -> 표면)"]
    for nm, L, k, w in LAYERS:
        lines.append("  %-13s L = %7.4f mm   k = %.3f   w = %.4f 1/s   kappa*L = %.4f"
                     % (nm, L * 1e3, k, w, kappa(k, w) * L))
    lines.append("  total thickness %.3f mm" % (L_TOT * 1e3))
    lines.append("  rho_b c_b = %.6g J/(m^3 K)   T_a = %.2f K   q_met = %.1f W/m^3"
                 % (RHO_CB, T_ARTERIAL, Q_MET))
    lines.append("  eps = %.2f   h = %.1f W/(m^2 K)   T_inf = T_env = %.2f K"
                 % (EPS_SKIN, H_CONV, T_INF))
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
