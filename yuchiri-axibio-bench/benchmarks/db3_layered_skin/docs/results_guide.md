# DB-3 수치해석 결과 설명서
# Reading the DB-3 numerical results

도면: `DB3_수치해석결과.png` (7패널)
계산: `yuchiri-axirad2D` v1.1.0, 9절점 사각형 요소
벤치마크: `yuchiri-axibio-bench` v0.1, `DB-3`

*한국어 먼저 · English follows*

---
---

# 한국어

## 0. 이 도면이 답하는 질문

> **코드가 이 방정식들을 맞게 푸는가?**

그것뿐입니다. "이 방정식이 실제 피부를 기술하는가"는 다른 문제이고, 여기서 답하지
않습니다. 생물학적 의미는 `DB3_생물학적_의미_설명서.md` 에 따로 있습니다.

## 1. 결론 먼저

| 항목 | 결과 | 판정 |
|---|---|---|
| 표면 온도, 정확해 대비 | 차이 **3.0e-10 ~ 7.0e-08 K** | 통과 |
| 절점 L∞ 오차 (최밀 격자) | **5.2e-10 ~ 1.1e-07 K** | 통과 |
| 관측 수렴 차수 `p` | **3.83 ~ 3.97** | 기대값 4 (§4) |
| 에너지 수지 상대 잔차 | **8.5e-13 ~ 1.1e-10** | 통과 |
| 허위 반경 변화 | **2.3e-13 ~ 2.8e-13 K** (정확해는 0) | 통과 |

---

## 2. 패널별 읽는 법

### (a) 온도 분포 — 정확해와 계산

`【사실】` 실선이 정확해, 흰 동그라미가 **가장 성긴 격자(h)** 의 계산 절점입니다.

`【해석】` 가장 성긴 격자에서도 점이 선 위에 정확히 놓입니다. 세 곡선이 갈라지는
것은 관류 배율(×0.1 / ×1 / ×10) 차이이며, 오차가 아닙니다.

`【해석】` 마지막 0.1 mm(표피)에서 기울기가 꺾이는 것이 보입니다. **관류가 0 인
층이라 방정식의 형태가 달라지기 때문**입니다. 이 꺾임을 코드가 제대로 잡아내는지가
이 벤치마크의 목적 중 하나입니다.

### (b) 격자 수렴 — **이 도면의 핵심**

`【사실】` 로그-로그에서 세 경우 모두 직선이며 기울기가 **3.83~3.97** 입니다.
회색 파선이 기울기 4 기준선입니다.

`【해석】` **합격 판정을 여기서 합니다.** 고정 허용오차가 아니라 수렴 차수로
판정하는 이유는, 허용오차가 **근거 없는 상수**이기 때문입니다 — 격자·요소 차수·문제
규모에 의존하는데 벤치마크가 그중 아무것도 통제하지 않습니다. 차수는 그렇지 않습니다.

`【사실】` **기대 차수가 3 이 아니라 4 인 이유** — 1차원에서 유한요소해의 **절점값**은
절점 사이의 장보다 빠르게 수렴합니다(절점 초수렴). 차수 `p` 요소에서 `O(h^{2p})` 이고,
`p = 2` 이면 4 입니다.

`【사실】` **이것이 사양서 초안의 오류를 잡았습니다.** 초안은 노름을 밝히지 않고
"2차 요소 → 3" 이라고 적었습니다. 실측이 4 에 가까웠고, 사양서 §4 를 정정했습니다.

### (c) 오차는 어디에 있는가

`【사실】` 깊이에 따른 `|T − T_exact|` 입니다. 세 곡선이 세분 단계입니다.

`【해석】` 오차가 **층 전체에 고르게 퍼져 있습니다.** 특정 지점에 몰려 있지 않다는
것은 **국소적 결함이 아니라 정상적인 이산화 오차**라는 뜻입니다. 만약 계면(파선)에서
치솟았다면 계면 처리에 문제가 있다는 신호였을 것입니다.

`【해석】` 아래로 뾰족하게 내려꽂히는 점들은 오차의 **부호가 바뀌는 지점**입니다.
로그 축이라 0 근처가 아래로 튑니다. 정상입니다.

### (d) Newton 수렴

`【사실】` 세 경우 모두 **3~4회**에 기계 정밀도에 도달합니다.

`【해석】` 이것이 **복사 야코비안이 옳다는 증거**입니다. `4εσT³` 항이 틀렸다면
수렴이 느려지거나 선형 수렴에 그칩니다. 발산하지 않으므로 육안으로는 알기 어렵고,
**수렴 속도만이 신호**입니다.

`【해석】` 관류가 강할수록(빨강) 더 빨리 수렴합니다. 관류 항이 야코비안에 **양의
정부호** 기여를 하기 때문입니다. 물리적으로도 맞습니다 — 열싱크는 온도장을 `T_a` 로
끌어당깁니다.

### (e) 2차원 온도장

`【사실】` `r` 방향으로 색이 전혀 변하지 않습니다.

`【해석】` **정확해에 반경 의존성이 없으므로 계산에도 없어야 합니다.** 측면이
단열이고, 축대칭에서 이는 자연 경계조건이라 아무 조치가 필요 없습니다. 반경 변화가
나타난다면 **`2πr` 가중치 처리에 문제**가 있다는 뜻입니다.

### (f) 허위 반경 변화

`【사실】` 세 경우, 세 격자 모두 **1e-13 수준**입니다. 시험 기준선(1e-9)보다
네 자릿수 아래입니다.

`【해석】` **이것이 이 벤치마크의 숨은 검사**입니다. 1차원 정확해를 2차원 코드로 푸는
구성을 일부러 골랐습니다. 축대칭 처리에 결함이 있으면 여기서 드러납니다.

### (g) 종합표

`【사실】` 최밀 격자에서의 모든 판정값입니다. **`κL` 열이 각 경우의 성격**을
말해 줍니다 — 피하지방의 `κL` 이 1.11 → 3.51 → 11.09 로 커지면서 열경계층이 얇아지고,
같은 격자에서 오차가 커집니다(5.2e-10 → 7.4e-09 → 1.1e-07).

`【해석】` **이 경향이 정상입니다.** `κL = 11` 은 얇은 층을 만들어 성긴 격자가
뭉갭니다. 그래서 벤치마크가 세 영역을 모두 훑도록 설계되어 있습니다. **`κa = 0.1`
에서만 통과한 코드는 시험된 것이 아닙니다.**

---

## 3. 이 결과가 증명하지 **않는** 것

`【사실】` 아래는 이 도면으로 알 수 없습니다.

* Pennes 식이 실제 조직을 기술하는지 — **확인(validation)이 아니라 검증입니다**
* 물성값이 실제 사람의 것인지 — 문헌값 조합 하나일 뿐입니다
* 과도 현상(화상, 순간 가열) — 이 계산은 **정상상태**입니다
* 3차원 효과, 대혈관, 증발 — 모두 범위 밖입니다

`【사실】` 계산된 표면 온도 36.30 °C 는 **실측 피부 온도(32~34 °C)보다 높습니다.**
이는 오류가 아니라 이 문제가 검증용 시나리오이기 때문입니다.

---
---

# English

## 0. The question this figure answers

> **Does the code solve these equations correctly?**

That is all. Whether the equations describe real skin is a different question and
is not answered here. For the biology see `DB3_생물학적_의미_설명서.md`.

## 1. Result first

| Quantity | Result | Verdict |
|---|---|---|
| Surface temperature vs exact | **3.0e-10 – 7.0e-08 K** | pass |
| Nodal L∞ error, finest mesh | **5.2e-10 – 1.1e-07 K** | pass |
| Observed order `p` | **3.83 – 3.97** | expected 4 |
| Energy balance residual | **8.5e-13 – 1.1e-10** | pass |
| Spurious radial variation | **2.3e-13 – 2.8e-13 K** (exact: 0) | pass |

## 2. Panel by panel

**(a) Profile.** Lines are exact, open circles are computed nodes on the
**coarsest** mesh. The kink in the last 0.1 mm is the epidermis, where perfusion
is zero and the form of the solution changes — catching that kink is part of the
point.

**(b) Convergence — the central panel.** Straight lines on log-log with slopes
**3.83–3.97**; the grey dashed line is slope 4. **Acceptance is decided here**,
by order rather than by a fixed tolerance, because a fixed tolerance is an
unjustified constant. The expected order is 4, not 3, because nodal values of a
1D finite element solution superconverge at `O(h^{2p})`. **This measurement caught
an error in the draft specification**, which had said 3 without naming the norm.

**(c) Where the error lives.** Spread evenly through the layers, not piled up at
an interface — that is ordinary discretisation error, not a local defect. The
downward spikes are sign changes plotted on a log axis.

**(d) Newton.** Machine precision in 3–4 iterations. **This is the evidence that
the radiative Jacobian is right**: a wrong `4εσT³` term slows convergence without
diverging, so speed is the only signal. Stronger perfusion converges faster
because the perfusion term is a positive-definite contribution to the Jacobian.

**(e) 2D field.** No colour variation in `r`. The exact solution has no radial
dependence, so neither should the computation.

**(f) Spurious radial variation.** ~1e-13 everywhere, four decades below the test
threshold. **This is the hidden check**: a one-dimensional exact solution was
deliberately posed to a two-dimensional code, so a defect in the axisymmetric
`2πr` weighting would show up here.

**(g) Summary.** The `κL` column explains the trend: as the subcutaneous `κL`
grows 1.11 → 3.51 → 11.09 the thermal layer thins and the error on the same mesh
grows 5.2e-10 → 7.4e-09 → 1.1e-07. **That trend is correct behaviour.** A code
that passes only at low `κa` has not been tested.

## 3. What this does **not** prove

Not whether Pennes describes real tissue; not whether the properties are those of
any real person; nothing about transients such as burns, since this is steady
state; and nothing about three-dimensional effects, large vessels or evaporation.

The computed surface temperature of 36.30 °C is **higher than measured skin
temperature** (32–34 °C). That is expected: this is a verification scenario, not a
calibrated model.
