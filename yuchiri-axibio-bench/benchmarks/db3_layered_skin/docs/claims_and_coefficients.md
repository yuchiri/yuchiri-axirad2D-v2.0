# Which claims do the coefficients actually support?
# 이 계수들이 실제로 뒷받침하는 주장은 무엇인가

A short report on the DB-3 benchmark. `yuchiri-axibio-bench` v0.2.
DB-3 벤치마크에 관한 짧은 보고서.

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## 0. The question

Several coefficients in this benchmark come from a single secondary source whose
primary origin has not been traced. It is therefore fair to ask: **if the inputs
are not fully sourced, what is anyone entitled to conclude from the outputs?**

The answer is not "nothing" and it is not "everything". It depends on the claim.
Different claims lean on different coefficients, and some lean on very few.

## 1. Two claims that look alike but are not

| | Claim | Verdict |
|---|---|---|
| **A** | In still indoor air, **radiation carries at least as much heat from a skin-like surface as convection does** | **Supported**, across the whole reported range of the coefficients |
| **B** | **Radiation is 55 % of the heat a person's skin loses** | **Not supported.** It is a statement about this model, not about a person |

The two are often stated in one breath. They should not be.

## 2. Why claim A survives

At the surface, with the air and the surrounding surfaces at the same
temperature,

```
q_rad / q_conv  =  ε σ (T_s⁴ − T_env⁴) / [ h (T_s − T_env) ]  ≈  4 ε σ T_m³ / h
```

**This ratio depends on `ε`, `σ`, `h`, and — only through `T_m³` — on `T_s`.**
It does not depend on the layer conductivities, the perfusion rate, the metabolic
rate, the blood heat capacity, the layer thicknesses or the core temperature.
**Every coefficient whose primary source was not traced lies in that second
list.** They reach the ratio only by shifting `T_s`, and `T_m³` moves by about
2 % across the whole plausible range of `T_s`.

The two coefficients that do matter are the two that are best supported:

* `ε` — Steketee (1973) measured skin emissivity over 1–14 µm as **0.98 ± 0.01**,
  independent of wavelength and of pigmentation; re-measured in 2009 by CO₂-laser
  reflection as 0.976 ± 0.006.
* `σ` — the Stefan–Boltzmann constant, fixed by the SI definitions.
* `h` — reported for whole-body natural convection as 5.1 (Colin & Houdas 1967),
  4.9/4.3 (Ichihara), 4.0 (Seppänen 1972), 3.4/3.3 (de Dear 1997), 3.3 (Omori
  2004), 3.1 (Mitchell 1974); per body segment the spread is 0.9–5.5.

Sweeping all of them together:

| `ε`, `h` | `T_s` = 30 °C | **32 °C** | **34 °C** | 36.3 °C | 37 °C |
|---|---|---|---|---|---|
| 0.95, **5.5** *(worst case)* | 1.059 | 1.070 | 1.081 | 1.094 | 1.097 |
| 0.98, 5.1 | 1.179 | 1.191 | 1.203 | 1.217 | 1.221 |
| **0.98, 5.0** *(this benchmark)* | 1.202 | 1.214 | 1.227 | **1.241** | 1.245 |
| 0.98, **3.4** *(modern consensus)* | 1.768 | 1.786 | 1.804 | 1.825 | 1.831 |
| 0.99, **3.1** *(best case)* | 1.959 | 1.979 | 1.999 | 2.022 | 2.029 |

**The ratio never falls below 1.** Worst case 1.06, best case 2.03. The columns
at 32 and 34 °C are the measured skin temperatures, so the conclusion does not
depend on this model getting `T_s` right.

Equivalently, `h_r = 4εσT_m³` lies in **5.83–6.29 W/(m²·K)** over that whole
sweep, while `h` lies in 3.1–5.1. The intervals do not overlap.

**One more thing is worth stating plainly.** The value used here, `h = 5.0`, is at
the **high** end of the reported range, which is the value least favourable to
claim A. Any other literature value strengthens it. That was not the reason it
was chosen — it was chosen so the benchmark would exercise both terms — but it is
a fact worth knowing when weighing the claim.

## 3. Why claim B does not survive

Two reasons, either sufficient.

1. **No evaporation is modelled here.** Real skin loses heat by insensible
   perspiration as well. That is a third output channel, so radiation's *share of
   the total* is necessarily smaller for a person than for this model. Note that
   evaporation enters the denominator only: it changes the share, not the
   radiation-to-convection ratio. Claim A is untouched.
2. **The share depends on `T_s`**, and `T_s` depends on exactly the coefficients
   whose primary sources were not traced.

The computed surface temperature here, 36.30 °C, is itself higher than measured
human skin at 32–34 °C in a 24 °C room. That difference is expected and stated
throughout this repository; it is also a direct warning against reading claim B
as being about a person.

## 4. Where claim A stops

Claim A is about **still indoor air**. Air movement raises `h` steeply:

| `h` [W/(m²·K)] | radiation's share |
|---|---|
| 5 (still) | **55 %** |
| 10 | 38 % |
| 15 | 29 % |
| 30 (strong airflow) | **17 %** |

So the sentence has to carry its condition. "Radiation matters as much as
convection" is true indoors in still air and false in a draught.

Claim A also assumes the surrounding surfaces are at air temperature. Cold walls
raise the radiative term further; warm walls lower it.

## 5. What this means for the benchmark

Nothing, in the following precise sense: **the benchmark's correctness does not
rest on any of this.** The reference is an exact solution of the stated
equations, and it is exact for whatever coefficients are stated. The coefficients
need only be fixed, physically admissible, and demanding enough to exercise the
terms under test — see `problem.md` section 3a.

What this report constrains is the **physical commentary** that surrounds the
benchmark. Claim A may be made. Claim B may not, at least not without an
evaporation model and sourced coefficients for it.

## 6. What is still not known

* The primary origin of the layer conductivities, the perfusion rate, the
  metabolic rate and the blood heat capacity. Each comes from a single secondary
  source, cited in `problem.md` section 3. For realistic values with documented
  spread, use the IT'IS database (Baumgartner et al., Version 5.0, DOI
  10.13099/VIP21000-05-0), not the values here.
* Radiation's share of a real person's heat loss, with evaporation included. Not
  computed; it would need an evaporation model and sourced coefficients for it.
* Whether `h = 5.0` or `h = 3.4` is the better description of the scenario
  intended. Both are in the literature; the benchmark states which it uses and
  why.

---
---

# 한국어

## 0. 질문

이 벤치마크의 계수 몇 개는 1차 출처를 추적하지 못한 단일 2차 문헌에서 왔다.
그러면 이렇게 묻는 것이 정당하다. **입력의 출처가 완전하지 않다면, 출력으로부터
무엇을 결론지을 수 있는가?**

답은 "아무것도 없다" 도 아니고 "전부" 도 아니다. **주장에 따라 다르다.** 주장마다
기대는 계수가 다르고, 어떤 주장은 아주 적은 계수에만 기댄다.

## 1. 비슷해 보이지만 다른 두 주장

| | 주장 | 판정 |
|---|---|---|
| **A** | 정지 실내 공기에서 **피부 같은 표면은 복사로 적어도 대류만큼 열을 잃는다** | **성립.** 계수의 보고 범위 전체에서 |
| **B** | **복사가 사람 피부 열손실의 55 %다** | **성립하지 않음.** 이 모델에 관한 진술이지 사람에 관한 진술이 아니다 |

둘은 한 호흡에 함께 말해지곤 한다. 그래서는 안 된다.

## 2. 주장 A 가 살아남는 이유

표면에서, 공기와 주위 표면이 같은 온도일 때

```
q_rad / q_conv  =  ε σ (T_s⁴ − T_env⁴) / [ h (T_s − T_env) ]  ≈  4 ε σ T_m³ / h
```

**이 비는 `ε`, `σ`, `h`, 그리고 `T_m³` 를 통해서만 `T_s` 에 의존한다.** 층별
전도도, 관류율, 대사 발열, 혈액 열용량, 층 두께, 심부 온도에는 의존하지 않는다.
**1차 출처를 추적하지 못한 계수는 전부 뒤쪽 목록에 있다.** 그것들은 `T_s` 를 옮기는
경로로만 이 비에 닿고, `T_s` 가 그럴듯한 범위를 다 훑어도 `T_m³` 는 약 2 % 변한다.

정작 중요한 두 계수는 가장 잘 뒷받침되는 둘이다.

* `ε` — Steketee (1973) 가 1–14 µm 에서 측정한 **0.98 ± 0.01**, 파장과 색소 침착에
  무관. 2009년 CO₂ 레이저 반사법 재측정 0.976 ± 0.006.
* `σ` — Stefan–Boltzmann 상수. SI 정의로 고정.
* `h` — 전신 자연대류 보고값 5.1 (Colin & Houdas 1967), 4.9/4.3 (Ichihara),
  4.0 (Seppänen 1972), 3.4/3.3 (de Dear 1997), 3.3 (Omori 2004),
  3.1 (Mitchell 1974). 부위별 0.9–5.5.

전부 함께 훑으면:

| `ε`, `h` | `T_s` = 30 °C | **32 °C** | **34 °C** | 36.3 °C | 37 °C |
|---|---|---|---|---|---|
| 0.95, **5.5** *(최악)* | 1.059 | 1.070 | 1.081 | 1.094 | 1.097 |
| 0.98, 5.1 | 1.179 | 1.191 | 1.203 | 1.217 | 1.221 |
| **0.98, 5.0** *(본 벤치마크)* | 1.202 | 1.214 | 1.227 | **1.241** | 1.245 |
| 0.98, **3.4** *(현대 합의치)* | 1.768 | 1.786 | 1.804 | 1.825 | 1.831 |
| 0.99, **3.1** *(최선)* | 1.959 | 1.979 | 1.999 | 2.022 | 2.029 |

**비가 1 아래로 내려가는 조합이 없다.** 최악 1.06, 최선 2.03. 32 와 34 °C 열은
실측 피부 온도이므로, **이 결론은 이 모델이 `T_s` 를 맞게 냈는지에 의존하지 않는다.**

같은 말로, `h_r = 4εσT_m³` 는 그 전 범위에서 **5.83–6.29 W/(m²·K)** 이고 `h` 는
3.1–5.1 이다. **두 구간은 겹치지 않는다.**

**한 가지를 분명히 적어 둔다.** 여기서 쓴 `h = 5.0` 은 보고 범위의 **높은** 쪽이며,
주장 A 에 **가장 불리한** 값이다. 다른 어떤 문헌값을 넣어도 주장이 강해진다. 그것이
이 값을 고른 이유는 아니었지만 — 두 항을 모두 시험하려고 고른 값이다 — 주장을
저울질할 때 알아 둘 만한 사실이다.

## 3. 주장 B 가 살아남지 못하는 이유

두 가지이며, 어느 하나만으로도 충분하다.

1. **여기에는 증발이 없다.** 실제 피부는 무감성 발한으로도 열을 잃는다. 세 번째
   출력 채널이므로, 사람에게서 **전체 대비 복사의 비중**은 이 모델보다 반드시
   작다. 증발은 분모에만 들어간다는 점에 유의하라 — 비중을 바꾸지 복사/대류 비를
   바꾸지 않는다. **주장 A 는 영향을 받지 않는다.**
2. **비중은 `T_s` 에 의존**하고, `T_s` 는 바로 1차 출처를 추적하지 못한 계수들에
   의존한다.

여기서 계산된 표면 온도 36.30 °C 자체가 24 °C 실내의 실측 피부 32–34 °C 보다 높다.
그 차이는 예상된 것이고 이 저장소 곳곳에 적혀 있으며, **주장 B 를 사람에 관한
진술로 읽지 말라는 직접적인 경고**이기도 하다.

## 4. 주장 A 가 멈추는 곳

주장 A 는 **정지 실내 공기**에 관한 것이다. 공기가 움직이면 `h` 가 가파르게 오른다.

| `h` [W/(m²·K)] | 복사 비중 |
|---|---|
| 5 (정지) | **55 %** |
| 10 | 38 % |
| 15 | 29 % |
| 30 (강한 기류) | **17 %** |

그러므로 문장은 조건을 달고 다녀야 한다. "복사가 대류만큼 중요하다" 는 **정지 공기의
실내에서 참이고 바람 부는 곳에서 거짓이다.**

주장 A 는 주위 표면이 공기 온도라는 것도 전제한다. 벽이 차가우면 복사 항이 더
커지고, 따뜻하면 작아진다.

## 5. 이것이 벤치마크에 대해 뜻하는 것

다음의 정확한 의미에서, 아무것도 아니다 — **벤치마크의 정당성은 위 어느 것에도
기대지 않는다.** 참조값은 명시된 방정식의 정확해이며, 어떤 계수를 명시하든 그
계수에 대해 정확하다. 계수는 고정되어 있고, 물리적으로 허용되며, 시험 대상 항을
실제로 시험할 만큼 까다로우면 된다 — `problem.md` 3a절.

이 보고서가 제약하는 것은 벤치마크를 둘러싼 **물리적 해설**이다. 주장 A 는 해도
된다. 주장 B 는 안 된다. 적어도 증발 모델과 그 계수의 출처가 없는 한.

## 6. 여전히 모르는 것

* 층별 전도도, 관류율, 대사 발열, 혈액 열용량의 1차 출처. 각각 단일 2차 문헌에서
  왔으며 `problem.md` 3절에 인용되어 있다. 변동까지 문서화된 현실적 값이 필요하면
  여기가 아니라 IT'IS 데이터베이스를 쓰라 (Baumgartner 외, Version 5.0, DOI
  10.13099/VIP21000-05-0).
* 증발을 포함한 실제 사람에서의 복사 비중. 계산하지 않았다. 증발 모델과 그 계수의
  출처가 있어야 한다.
* 의도한 시나리오를 `h = 5.0` 과 `h = 3.4` 중 무엇이 더 잘 기술하는지. 둘 다
  문헌에 있으며, 벤치마크는 어느 것을 쓰는지와 그 이유를 밝힌다.
