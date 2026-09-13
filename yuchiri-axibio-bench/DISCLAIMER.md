# DISCLAIMER — No-warranty notice and statement of intended use
# 무보증 고지 및 사용 목적 선언

**This document is intended to be read independently of the licence.**
It is intended to apply regardless of whether copyright subsists in any part of
this repository and regardless of the validity of the licence.

**이 문서는 라이선스와 별개로 읽히도록 의도되었다.** 이 저장소의 어느 부분에
저작권이 성립하는지, 라이선스가 유효한지와 무관하게 적용될 것을 의도한다.

---
---

# English

## 1. This is not a medical device and has no medical purpose

**This software has no intended medical purpose.** It is not intended for the
diagnosis, prevention, monitoring, prediction, prognosis, treatment or
alleviation of disease or injury, in any person. It is not intended to inform any
clinical decision, and it must not be used for one.

It computes solutions of a heat transfer equation and compares them with a
mathematical reference. That is its entire purpose.

The word "skin" appears throughout because the benchmark's geometry and
properties are drawn from the literature on skin. **That is a choice of test
case, not a clinical claim.** See section 4.

## 2. No warranty

Provided **"AS IS", without warranty of any kind** — no warranty of
merchantability, of fitness for a particular purpose, or of non-infringement.

The author is **not liable for any damages** arising from the use of, or
inability to use, this material: direct, indirect, incidental or consequential,
including data loss, equipment damage, personal injury and business loss.

## 3. Verification, not validation

In the sense of ASME V&V 40:

| | Question | Answered here |
|---|---|---|
| Verification | Does a code solve the stated equations correctly? | **Yes** |
| Validation | Do those equations describe real tissue? | **No** |

**The Pennes bioheat equation is a modelling hypothesis, not a law of nature.**
Passing every benchmark in this suite says nothing about whether that equation
describes any real tissue, in any person, under any condition.

## 3a. The blood term is not convection

There is no velocity field and no advection term in this benchmark. The Pennes
perfusion term is a **lumped** stand-in for blood–tissue heat exchange, assuming
blood arrives at arterial temperature, equilibrates completely with the local
tissue, and leaves at the local temperature. It has no direction. Advection,
large vessels, counter-current artery–vein exchange and temperature-dependent
perfusion are all **outside the scope**. See `problem.md` section 4a.

## 4. The numbers here are not measurements of a person

The computed surface temperature at nominal perfusion is **309.45 K (36.30 °C)**.
Measured human skin in a 24 °C room sits at about **32–34 °C**. The difference is
expected and is not an error: this is a self-consistent verification scenario, not
a calibrated model of a forearm.

**No evaporation is modelled.** The surface loses heat here by convection and
radiation and by nothing else. Insensible perspiration and sweat are mass
transfer, which this suite does not treat. A real skin balance carries that
output term as well, so the surface here necessarily runs warmer than a measured
one. That is not the only reason for the difference, and the size of each
contribution has not been computed.

Tissue property values differ substantially between research fields and between
standards. The set used here is **one internally consistent set**, chosen so that
the benchmark exercises the terms it is meant to exercise. It is not *the* value
of anything. **If you need realistic tissue values, take them from the IT'IS
database** (Baumgartner et al., Version 5.0, DOI 10.13099/VIP21000-05-0), not
from here; it reports averages with standard deviations and the number of studies
behind each one. A coefficient in a verification benchmark only has to be fixed,
physically admissible, and demanding enough to exercise the terms under test —
see `problem.md` section 3a. Every value is marked in `problem.md` as either taken from the
literature, with the source recorded, or chosen by this benchmark, with the reason
recorded.

## 5. Do not use this as evidence

Not for safety-related calculations. Not for regulatory submissions. Not as
design evidence for medical devices, thermal therapy equipment, protective
clothing, or anything else on which a person's safety depends. For such purposes
use tools carrying the verification, validation and quality-assurance regime that
the relevant field requires.

## 6. AI use

Written using Anthropic's Claude as a tool; the design decisions were made by the
human author. This changes nothing in the statements above.

## 7. Before you rely on any result

1. Run `exact/run_reference.py` on your own machine and confirm the four
   self-checks pass and the reference values match those committed here.
2. Run `exact/check_report.py` on your own report and read the reasons, not only
   the verdict.
3. Vary the mesh. The acceptance criterion is an **order of convergence**, not a
   tolerance; a single mesh proves nothing.
4. Remember section 3.

---
---

# 한국어

## 1. 의료기기가 아니며 의료 목적이 없다

**이 소프트웨어에는 의도된 의료 목적이 없다.** 어떤 사람에 대해서도 질병이나 상해의
진단·예방·감시·예측·예후·치료·완화를 목적으로 하지 않는다. 어떤 임상적 판단에도
정보를 제공할 의도가 없으며, 그런 목적으로 사용해서는 안 된다.

이것은 열전달 방정식의 해를 계산하고 수학적 참조값과 대조한다. 그것이 목적의
전부다.

문서 전체에 "피부" 라는 말이 나오는 것은, 벤치마크의 형상과 물성을 피부에 관한
문헌에서 가져왔기 때문이다. **시험 문제의 선택이지 임상적 주장이 아니다.** 4절 참조.

## 2. 무보증

**아무런 보증 없이 "있는 그대로"** 제공된다. 상품성, 특정 목적 적합성, 비침해에
대한 어떤 보증도 하지 않는다.

작성자는 이 자료의 사용 또는 사용 불능으로 발생하는 **어떤 손해에 대해서도 책임지지
않는다.** 직접·간접·부수적·결과적 손해, 데이터 손실, 장비 손상, 인적 피해, 영업
손실을 포함하며 이에 한정되지 않는다.

## 3. 검증이지 확인이 아니다

ASME V&V 40 의 용어로:

| | 질문 | 여기서 답하는가 |
|---|---|---|
| 검증 | 코드가 명시된 방정식을 맞게 푸는가 | **예** |
| 확인 | 그 방정식이 실제 조직을 기술하는가 | **아니오** |

**Pennes 생체열방정식은 자연 법칙이 아니라 모델 가설이다.** 이 모음의 모든
벤치마크를 통과해도, 그 식이 어떤 사람의 어떤 조직을 어떤 조건에서 기술하는지에
대해서는 아무것도 말해 주지 않는다.

## 3a. 혈류 항은 대류가 아니다

이 벤치마크에는 속도장도 이류항도 없다. Pennes 관류 항은 혈액–조직 열교환을
**뭉뚱그린 대역**이며, 혈액이 동맥 온도로 들어와 국소 조직과 완전히 열평형에 이른 뒤
국소 온도로 나간다고 가정한다. 방향이 없다. 이류, 대혈관, 동맥–정맥 역류 열교환,
온도 의존 관류는 모두 **범위 밖**이다. `problem.md` 4a절 참조.

## 4. 여기의 숫자는 사람을 측정한 값이 아니다

공칭 관류에서 계산된 표면 온도는 **309.45 K (36.30 °C)** 다. 24 °C 실내에서 실측되는
사람의 피부는 약 **32~34 °C** 다. 이 차이는 예상된 것이며 오류가 아니다. 자기정합적인
검증 시나리오이지 전완을 보정한 모델이 아니다.

**증발은 모델링하지 않는다.** 여기서 표면은 대류와 복사로만 열을 잃는다. 무감성
발한과 땀은 물질전달이며 이 모음이 다루지 않는다. 실제 피부의 수지에는 그 출력 항이
더 있으므로, 여기의 표면은 필연적으로 실측보다 따뜻하게 나온다. 차이의 유일한
이유는 아니며, 각 요인의 기여 크기는 계산하지 않았다.

조직 물성값은 연구 분야마다, 표준마다 상당히 다르다. 여기서 쓴 조합은 **내적으로
정합적인 하나의 조합**이며, 벤치마크가 시험하려는 항을 실제로 시험하도록 고른 것이다.
무엇의 *그* 값도 아니다. **현실적인 조직 물성이 필요하면 여기가 아니라 IT'IS
데이터베이스에서 가져오라** (Baumgartner 외, Version 5.0, DOI 10.13099/VIP21000-05-0).
값마다 평균·표준편차·근거 논문 수를 제공한다. 검증 벤치마크의 계수는 고정되어 있고,
물리적으로 허용되며, 시험 대상 항을 실제로 시험할 만큼 까다로우면 된다 —
`problem.md` 3a절 참조. 모든 값은 `problem.md` 에 문헌에서 가져온 것(출처 기록)인지
이 벤치마크가 정한 것(이유 기록)인지 표시되어 있다.

## 5. 근거로 사용하지 말 것

안전 관련 계산에 쓰지 말 것. 규제 제출에 쓰지 말 것. 의료기기, 온열치료 장비,
보호복, 그 밖에 사람의 안전이 걸린 어떤 것의 설계 근거로도 쓰지 말 것. 그런 용도에는
해당 분야가 요구하는 검증·확인·품질보증 체계를 갖춘 도구를 사용하라.

## 6. AI 사용

Anthropic 의 Claude 를 도구로 사용해 작성했으며, 설계 결정은 사람이 내렸다.
이 사실이 위 서술의 어떤 부분도 바꾸지 않는다.

## 7. 어떤 결과에 의존하기 전에

1. 자기 컴퓨터에서 `exact/run_reference.py` 를 돌려 자체 검사 4건이 통과하고
   참조값이 여기 커밋된 것과 일치하는지 확인하라.
2. 자기 보고서에 `exact/check_report.py` 를 돌리고, 판정만이 아니라 이유를 읽어라.
3. 격자를 바꿔 보라. 합격 기준은 허용오차가 아니라 **수렴 차수**다. 격자 하나로는
   아무것도 증명되지 않는다.
4. 3절을 기억하라.
