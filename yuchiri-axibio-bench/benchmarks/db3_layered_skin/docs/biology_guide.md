# DB-3 결과의 생물학적 의미
# What the DB-3 numbers mean biologically

도면: `DB3_생물학적_의미.png`
계산: `yuchiri-axirad2D` v1.1.0 · 벤치마크 `yuchiri-axibio-bench` DB-3

*한국어 먼저 · English follows*

---
---

# 한국어

## 0. 한 문장으로

> **피부가 잃는 열의 97 %는 혈액이 실어 온 것이고, 몸은 혈류를 조절해 표면 온도를
> 1.7 °C 움직인다. 열은 조직 속으로 겨우 1~2 mm 밖에 스며들지 못한다.**

아래는 그 세 문장을 계산 결과에서 하나씩 풀어 쓴 것입니다.

---

## 1. 계산이 내놓은 숫자

정상 관류에서:

| 항목 | 값 |
|---|---|
| 피부 표면 온도 | **36.30 °C** (309.45 K) |
| 표면에서 나가는 열 | **137.8 W/m²** |
| 그중 복사 | 76.3 W/m² (**55.4 %**) |
| 그중 대류 | 61.5 W/m² (44.6 %) |

혈류를 바꾸면:

| 상태 | 관류 배율 | 표면 온도 | 표면 방열 |
|---|---|---|---|
| **혈관수축** (추울 때) | ×0.1 | **35.09 °C** | 123.8 W/m² |
| 정상 | ×1 | 36.30 °C | 137.8 W/m² |
| **혈관확장** (더울 때) | ×10 | **36.74 °C** | 142.9 W/m² |

---

## 2. 첫 번째 의미 — 피부는 난로가 아니라 방열판이다

`【사실】` 피부가 표면으로 내보내는 137.8 W/m² 가 **어디서 왔는지** 계산이 알려 줍니다.

| 공급원 | 값 | 비율 |
|---|---|---|
| **혈액이 실어 온 열** | 133.2 W/m² | **96.7 %** |
| 심부에서 전도로 | 2.8 W/m² | 2.0 % |
| 피부 자신의 대사 | 1.8 W/m² | 1.3 % |

`【해석】` **피부 자신이 만드는 열은 전체의 1.3 % 뿐입니다.** 나머지는 거의 전부
혈액이 심부에서 실어 온 것입니다.

`【해석】` 이것이 **관류 항이 왜 생체열전달의 핵심인가**에 대한 답입니다. 조직을
"전도만 하는 고체"로 보면 열이 어디서 오는지 설명할 수 없습니다. 방정식에 관류 항이
없으면 **97 %를 놓치는 것**입니다.

> 실용적 함의 — 조직을 단순 전도체로 모델링한 계산은, 그 조직에 혈류가 있는 한
> **거의 확실히 틀립니다.**

---

## 3. 두 번째 의미 — 혈류가 체온조절의 손잡이다

`【사실】` 관류를 100배 바꾸면(×0.1 → ×10) 표면 온도가 **35.09 → 36.74 °C**, 즉
**1.65 °C** 움직입니다. 방열량은 123.8 → 142.9 W/m², **15 % 증가**합니다.

`【해석】` **몸이 실제로 하는 일이 이것입니다.** 추우면 말초 혈관을 좁혀 표면 온도를
낮추고 — 표면이 차가우면 환경과의 온도차가 줄어 열을 덜 잃습니다. 더우면 혈관을 넓혀
표면을 뜨겁게 하고 열을 더 버립니다. **심부 온도 37 °C 를 지키기 위해 표면 온도를
희생하는 구조**입니다.

`【해석】` 도면 왼쪽에서 파란 곡선(혈관수축)만 심부에서부터 크게 떨어지는 것이 보입니다.
혈류가 적으면 열이 **전도로만** 올라와야 하고, 전도는 느리기 때문입니다.

> 실용적 함의 — 적외선 체온계나 웨어러블이 재는 **피부 온도는 심부 체온이 아닙니다.**
> 같은 사람이 같은 심부 온도에서도 혈류 상태에 따라 **1.7 °C 차이**가 납니다.

---

## 4. 세 번째 의미 — 열은 몇 mm 밖에 못 간다

`【사실】` 관류가 있는 조직에는 **열침투깊이** `1/κ` 라는 고유 길이가 있습니다.

```
κ = √( 관류율 × 혈액 열용량 / 열전도도 )
```

| 상태 | 진피 `1/κ` | 피하 `1/κ` |
|---|---|---|
| 혈관수축 ×0.1 | 4.94 mm | 3.25 mm |
| **정상 ×1** | **1.56 mm** | **1.03 mm** |
| 혈관확장 ×10 | 0.49 mm | 0.33 mm |

`【해석】` **이 거리를 넘어가면 온도 교란이 `1/e` 로 줄어듭니다.** 정상 관류에서
1~1.6 mm 입니다. 즉 **피부 표면에서 무슨 일이 일어나도 몇 mm 아래는 거의 모릅니다.**
혈액이 계속 37 °C 로 되돌려 놓기 때문입니다.

`【해석】` 그리고 **혈류가 많을수록 열침투깊이가 짧아집니다.** 관류가 10배면
`1/κ` 는 √10 ≈ 3.2배 짧아집니다.

> 실용적 함의 1 — **온열치료·소작에서 혈류는 적입니다.** 혈류가 풍부한 종양은 열을
> 곧바로 실어 내가므로 데우기 어렵습니다. 임상에서 관류가 치료 저항성의 요인으로
> 다뤄지는 이유가 이 한 줄에 있습니다.
>
> 실용적 함의 2 — **국소 가열은 국소에 머뭅니다.** 프로브 주위 mm 단위로만 퍼지므로
> 정밀 제어가 가능한 반면, 조금만 벗어나도 온도가 급락합니다.
>
> 실용적 함의 3 — **얕은 화상과 깊은 화상의 경계**가 이 길이척도와 관련됩니다.
> 다만 화상은 짧은 과도 현상이라 정상상태인 이 계산이 직접 답하지는 않습니다(§7).

---

## 5. 네 번째 의미 — 복사가 대류보다 많다

`【사실】` 24 °C 실내에서 표면 방열의 **55.4 %가 복사**, 44.6 %가 대류입니다.

`【해석】` 직관과 어긋날 수 있습니다. "바람이 없으면 열을 안 잃는다"고 생각하기
쉽지만, 몸은 **아무것도 닿지 않아도 벽을 향해 빛(적외선)으로 열을 버립니다.**

`【해석】` 그래서 같은 기온이라도 **벽이 차가운 방이 더 춥게 느껴집니다.** 복사는
공기 온도가 아니라 **주위 표면 온도**를 봅니다. 건축·공조에서 평균복사온도(MRT)를
따로 다루는 이유입니다.

> 실용적 함의 — 적외선 열화상은 이 복사를 재는 것입니다. 피부 방사율이 0.98 로
> 높아 **거의 흑체처럼 행동**하며, 그래서 열화상 체온 측정이 성립합니다.

---

## 6. 표피가 특별한 이유

`【사실】` 표피는 **혈관이 없습니다.** 그래서 계산에서 관류율이 정확히 0 입니다.

`【해석】` 열적으로 표피는 **혈액이 손대지 못하는 얇은 담요**입니다. 다른 층은 혈액이
온도를 37 °C 로 끌어당기지만, 표피는 순수 전도만으로 온도가 떨어집니다. 도면에서
마지막 0.1 mm 구간의 기울기가 급해지는 것이 그것입니다.

`【해석】` 계산 코드 입장에서도 이 층이 특별합니다. **관류가 0 이면 지배방정식의
형태 자체가 바뀝니다**(지수함수 → 2차 다항식). 벤치마크가 이 층을 일부러 넣은 이유는,
그 분기를 시험하기 위해서입니다.

---

## 7. ★ 이 숫자를 어디까지 믿어야 하는가

`【사실】` **계산된 표면 온도 36.30 °C 는 실측 피부 온도보다 높습니다.** 24 °C 실내에서
사람 피부는 보통 **32~34 °C** 입니다.

`【해석】` 이것은 오류가 아니라 **의도된 한계**입니다. 이 문제는 **검증(verification)**
용으로 설계되었습니다 — "코드가 방정식을 맞게 푸는가"를 묻지, "이 방정식이 실제 피부를
맞게 기술하는가"를 묻지 않습니다.

`【사실】` 실제와 다른 이유는 최소 넷입니다.

| # | 이유 |
|---|---|
| 1 | **Pennes 식 자체가 가설**입니다. 혈액이 모세혈관에서 조직 온도와 완전히 평형을 이룬다고 가정하는데, 굵은 혈관에서는 그렇지 않습니다 |
| 2 | **두께 4.9 mm 는 전완 기준**입니다. 부위마다 크게 다릅니다 |
| 3 | **땀에 의한 증발**을 넣지 않았습니다. 실제 피부는 무감성 발한으로도 열을 잃습니다 |
| 4 | **물성값이 문헌마다 다릅니다.** 우리가 쓴 것은 정합적인 *하나의* 조합이지 *그* 값이 아닙니다 |

`【사실】` 그리고 **이 계산은 정상상태입니다.** 화상처럼 수 초 단위 현상은 다룰 수
없습니다. 문헌에 "관류는 화상 손상에 큰 영향이 없다"는 서술이 있는데, 그것은 **짧은
노출**에 관한 것입니다 — 피부가 혈류를 늘려 반응하는 데 20 초쯤 걸리기 때문입니다.
**정상상태인 우리 문제에서는 정반대로 관류가 지배적입니다.**

`【해석】` 이 대비 자체가 교훈입니다. **같은 물리, 같은 방정식이라도 시간 규모가
다르면 결론이 뒤집힙니다.** 문헌의 결론을 맥락 없이 가져오면 틀립니다.

---

## 8. 그래서 이 계산이 증명한 것

`【사실】` 정확히 이것입니다.

> **코드가 다층 관류 조직에서 전도·관류·대사·대류·복사가 결합된 방정식을 맞게
> 푼다는 것.** 최밀 격자에서 정확해와의 차이가 **7.4e-09 K**, 관측 수렴 차수 **3.90**,
> 허위 반경 변화 **2.8e-13 K**.

`【해석】` 그 이상도 이하도 아닙니다. 그러나 그것이 **실제 조직 문제로 가기 전에
반드시 있어야 할 바닥**입니다. 방정식을 못 푸는 코드로는 어떤 생물학도 할 수 없습니다.

---
---

# English

## 0. In one sentence

> **97 % of the heat the skin loses arrived by blood; the body moves its surface
> temperature by 1.7 °C simply by changing blood flow; and heat penetrates only
> one or two millimetres into perfused tissue.**

## 1. The numbers

At nominal perfusion: surface **36.30 °C**, losing **137.8 W/m²**, of which
**55.4 % is radiation** and 44.6 % convection.

Changing blood flow:

| State | Perfusion | Surface T | Surface loss |
|---|---|---|---|
| **Vasoconstriction** (cold) | ×0.1 | **35.09 °C** | 123.8 W/m² |
| Nominal | ×1 | 36.30 °C | 137.8 W/m² |
| **Vasodilation** (hot) | ×10 | **36.74 °C** | 142.9 W/m² |

## 2. The skin is a radiator, not a furnace

Where the 137.8 W/m² comes from:

| Source | Value | Share |
|---|---|---|
| **Carried in by blood** | 133.2 W/m² | **96.7 %** |
| Conducted from the core | 2.8 W/m² | 2.0 % |
| The skin's own metabolism | 1.8 W/m² | 1.3 % |

The skin generates only 1.3 % of what it sheds. **A model that treats perfused
tissue as a simple conductor misses 97 % of the energy path.**

## 3. Blood flow is the thermostat's handle

A hundredfold change in perfusion moves the surface by **1.65 °C** and the heat
loss by 15 %. That is what the body actually does: constrict to keep heat in,
dilate to throw it away, **sacrificing surface temperature to protect the core at
37 °C**.

Practical consequence: a **skin temperature is not a core temperature.** The same
person at the same core temperature can read 1.7 °C differently depending on
peripheral blood flow.

## 4. Heat only travels a few millimetres

Perfused tissue has an intrinsic **thermal penetration depth** `1/κ`, with
`κ = √(perfusion × blood heat capacity / conductivity)`:

| State | Dermis | Subcutaneous |
|---|---|---|
| ×0.1 | 4.94 mm | 3.25 mm |
| **×1** | **1.56 mm** | **1.03 mm** |
| ×10 | 0.49 mm | 0.33 mm |

Beyond that distance a temperature disturbance falls by `1/e`. **More blood flow
means shorter reach** — tenfold perfusion shortens it by √10.

Practical consequences: in hyperthermia and ablation **blood flow is the enemy**,
because a well-perfused tumour carries the heat away as fast as you deliver it;
and local heating stays local, which is good for precision and bad for margins.

## 5. Radiation beats convection

In a 24 °C room, **55.4 % of the surface loss is radiation**. The body sheds heat
as infrared light to the walls even in still air. This is why a room with cold
walls feels cold at the same air temperature, and why infrared thermography works
at all — skin behaves nearly as a black body.

## 6. Why the epidermis is different

The epidermis has **no blood vessels**, so its perfusion is exactly zero. Blood
cannot reach it; thermally it is a thin blanket in which temperature falls by pure
conduction. In the equations, zero perfusion **changes the form of the solution**
from exponential to quadratic — which is precisely why the benchmark includes such
a layer.

## 7. How far to trust these numbers

**The computed 36.30 °C is higher than measured skin temperature** (typically
32–34 °C in a 24 °C room). This is a **verification** scenario: it asks whether
the code solves the equations, not whether the equations describe skin.

Four reasons it differs from reality: the Pennes equation is itself a hypothesis;
the 4.9 mm stack is forearm-like and body sites differ; evaporative loss is not
modelled; and published tissue properties differ substantially between fields.

Note also a trap. The literature reports that perfusion has little influence on
**burn** injury — but that concerns exposures of a few seconds, and the skin takes
about 20 s to increase blood flow. **In this steady problem perfusion is
dominant.** The same physics, at a different time scale, reverses the conclusion.

## 8. What the calculation therefore proves

Exactly this: that the code correctly solves conduction, perfusion, metabolism,
convection and radiation coupled together in a layered perfused tissue — nodal
error **7.4e-09 K** on the finest mesh, observed order **3.90**, spurious radial
variation **2.8e-13 K**.

No more than that. But it is the floor that has to be there before any of the
biology can be argued about.
