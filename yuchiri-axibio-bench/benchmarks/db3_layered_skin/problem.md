# DB-3 — Layered skin with perfusion and radiative surface loss
# DB-3 — 관류가 있는 다층 피부와 복사 표면 손실

Suite version 0.2.0 · `benchmark_id = DB-3`

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## 1. What this benchmark is for

It verifies that a solver correctly handles, **together in one problem**:

* the **Pennes perfusion sink** `ω_b ρ_b c_b (T_a − T)`, including a layer where
  perfusion is exactly zero;
* **layered materials** with different conductivity and perfusion;
* a **convective** surface boundary condition;
* a **radiative** surface boundary condition, which is nonlinear and contributes
  `4εσT³` to the Jacobian;
* the **axisymmetric weighting** — the exact solution has no radial dependence, so
  any radial variation in the computed field is a defect signal.

**It is verification, not validation.** It says nothing about whether the Pennes
equation describes real skin. See §7.

## 2. Geometry

A cylinder of radius `R`, thickness `L_tot`, layered along the axis. The lateral
surface is adiabatic, which in an axisymmetric formulation is the natural
condition and requires no action.

```
  x = L_tot   ┌───────────────┐  surface : convection + radiation
              │   epidermis   │  ω = 0   (avascular)
              ├───────────────┤
              │    dermis     │
              ├───────────────┤
              │ subcutaneous  │
  x = 0       └───────────────┘  core    : Dirichlet T_core
              |<——— R ———>|        lateral : adiabatic
```

## 3. Properties, and where each number comes from

`【LIT】` taken from the literature, source recorded.
`【SCENARIO】` chosen by this benchmark, reason recorded.

**The distinction is one of kind, not of availability.** Emissivity, convection
coefficient and ambient temperature describe the *situation*; a benchmark author
may set those. Tissue properties describe the *tissue*; a benchmark author may not
invent those.

| Quantity | Value | Origin |
|---|---|---|
| `k` epidermis / dermis / subcutaneous | 0.21 / 0.37 / 0.16 W/(m·K) | `【LIT】` Parvin et al., *Engineering Reports* (Wiley, 2025), three-layer skin model |
| perfusion, epidermis | **0** | `【LIT】` The epidermis has no blood vessels; the perfusion term is discarded there in skin bioheat models |
| perfusion, dermis and subcutaneous | 0.038 s⁻¹ | `【LIT】` reported range 0–0.1 mL blood/mL tissue/s, taken as 0.038 (*Sci. Rep.* 8, 2018) |
| `ρ_b c_b` | 1060 × 3770 = 3.9962e6 J/(m³·K) | `【LIT】` blood density and specific heat, same source |
| `q_met` | 368.1 W/m³ | `【LIT】` same source |
| `T_core = T_a` | 310.15 K (37 °C) | `【LIT】` blood and core body temperature, same source |
| thickness ratios | dermis ≈ 12 × epidermis, subcutaneous ≈ 3 × dermis | `【LIT】` inner-forearm proportions (Electronics Cooling, 2023) |
| thickness absolute scale | epidermis 0.1 mm → total 4.9 mm | `【SCENARIO】` ratios are from the literature; the absolute scale varies by body site, so one value must be picked |
| `ε` | 0.98 | `【LIT】` Steketee (1973), *Spectral emissivity of skin and pericardium*: measured over 1–14 µm as **0.98 ± 0.01**, independent of wavelength and of pigmentation. Re-measured 2009 by CO₂-laser reflection as 0.976 ± 0.006. Holds in the long-wave infrared, which is where a body near room temperature radiates; in the 3–5 µm band 0.91–0.92 has been proposed instead |
| `h` | 5 W/(m²·K) | `【SCENARIO, inside the reported range】` whole-body natural convection has been reported as 5.1 (Colin & Houdas 1967), 4.9/4.3 (Ichihara), 4.0 (Seppänen 1972), 3.4/3.3 (de Dear 1997), 3.3 (Omori 2004), 3.1 (Mitchell 1974); per segment the spread is 0.9–5.5. **5.0 is inside that range but at its high end.** Chosen so convection and radiation come out comparable — see §3a |
| `T_∞ = T_env` | 297.15 K (24 °C) | `【SCENARIO】` room condition; one number defines the environment |
| `R` | 5 mm | `【SCENARIO】` arbitrary — the exact solution does not depend on it |

**Literature values for skin differ substantially between research fields.** The
set above is *one* consistent set, not *the* values.

### 3a. On the two surface coefficients, and why these numbers are defensible

**The linearised radiative coefficient.** Here `4εσT_m³ = 6.20 W/(m²·K)` at
`T_m = 303.3 K`, while the measured **whole-body** radiative coefficient is about
4.5–4.7 W/(m²·K). These do not contradict each other: the whole-body figure
carries an effective-radiating-area factor of roughly 0.7, because limbs face one
another rather than the room. This benchmark poses a **flat** surface, for which
that factor is 1, so 6.20 is the right number for the geometry as stated.

**Why the coefficients are defensible for a verification benchmark.** A
coefficient here has to satisfy three things, and being a best estimate of real
tissue is not one of them.

| # | Requirement | Why |
|---|---|---|
| 1 | **Fixed and published** | The exact solution is a function of these numbers. If they drift, the reference is not reproducible |
| 2 | **Physically admissible** — right sign, right order, inside reported ranges | Otherwise the equations are solved in a non-physical regime and verifying them means nothing |
| 3 | **Exercises the terms under test** | A large `h` hides radiation; a small `ω` hides perfusion. Here `κL` = 3.51 / 0.77 / 0 and the surface splits 55 % radiation to 45 % convection |

The reference is an **exact solution of the stated equations, not a measurement**.
Whatever coefficients are put in, the exact solution is exact for them. The
realism of the coefficients therefore does not affect the correctness of the
reference; it affects **validation**, which this suite explicitly does not claim
(§7, and `DISCLAIMER.md` section 3).

**If you need realistic tissue values**, do not take them from here. Use the
IT'IS database: Baumgartner et al., *IT'IS Database for thermal and
electromagnetic parameters of biological tissues*, Version 5.0, 21 August 2025,
DOI 10.13099/VIP21000-05-0, `itis.swiss/database`. It reports averages with
standard deviations, ranges and the number of studies behind each value — and it
warns that for some parameters, perfusion in particular, the spread is large
enough to affect simulation results severely.

**What is not traced.** The layer conductivities, the perfusion rate, the
metabolic rate and the blood heat capacity each come from a single secondary
source, cited above; their primary origin has not been traced further. That is a
limitation of this documentation, not of the benchmark: requirement 1 above is
what the benchmark rests on, and it is satisfied because the values are fixed in
`exact/db3_properties.py` and regenerated by `exact/run_reference.py`.

## 4. Governing equation and the dimensionless groups

```
d/dx ( k_i dT/dx ) + ω_i ρ_b c_b ( T_a − T ) + q_met,i = 0        in layer i
κ_i = √( ω_i ρ_b c_b / k_i )
```

The solution is governed by `κ_i L_i` per layer:

| Layer | `κ_i L_i` at nominal perfusion |
|---|---|
| subcutaneous | 3.5072 |
| dermis | 0.7688 |
| epidermis | 0 |

Three cases are run by scaling the perfusion, to span the regimes:

| Case | scale | subcutaneous `κL` | character |
|---|---|---|---|
| weak | ×0.1 | 1.109 | conduction-dominated |
| nominal | ×1 | 3.507 | balanced |
| strong | ×10 | 11.09 | thin thermal layer near the core side |

### 4a. What the perfusion term is, and what it is not

**It is not convection.** There is no velocity field and no advection term
`v·∇T` anywhere in this benchmark or in any code that solves it as posed. The
Pennes term is a **lumped** stand-in for blood–tissue heat exchange: blood is
assumed to arrive at `T_a`, come fully into thermal equilibrium with the local
tissue, and leave at the local temperature. The model does not know which way
the blood is flowing.

Within the tissue, therefore, **conduction is the only transport mechanism**;
perfusion is a distributed source that feeds it. The three mechanisms act in
different places and should be compared separately.

| Mechanism | Where | How it is treated | Size in this problem |
|---|---|---|---|
| **Blood** | inside the tissue | volumetric source, **no advection** | supplies **133.2 W/m²** |
| **Conduction** | inside the tissue | solved | **the only transport**: 2.8 W/m² at the core boundary, 137.8 W/m² at the surface |
| **Air convection** | at the surface | boundary condition `h(T_s − T_∞)` | 61.5 W/m² (44.6 %) |
| **Radiation** | at the surface | nonlinear boundary condition | 76.3 W/m² (55.4 %) |
| Metabolism | inside the tissue | volumetric source | 1.8 W/m² (1.3 %) |

The conduction flux grows fiftyfold across the stack precisely because perfusion
keeps adding to it along the way. In the epidermis, where perfusion is zero,
conduction alone carries the full 137.8 W/m².

Relative strength of perfusion to conduction over a layer of thickness `L`:

| Layer | `κL` | `(κL)²` = perfusion / conduction |
|---|---|---|
| subcutaneous | 3.507 | **12.30** — perfusion dominates |
| dermis | 0.769 | 0.591 — comparable |
| epidermis | 0 | 0 — conduction only |

**Not represented**: advection and any velocity field; large vessels;
counter-current artery–vein exchange; temperature-dependent perfusion `ω(T)`,
and therefore no feedback of heating on blood flow.

**And on the output side: no evaporation.** The surface here loses heat by
convection and radiation and by nothing else. Insensible perspiration and sweat
are mass transfer, which is outside a heat-transfer benchmark; respiratory loss
is outside a skin balance altogether. The balance that closes in this problem is

```
blood 133.2  +  metabolism 1.8  +  conduction from the core 2.8
        =  convection 61.5  +  radiation 76.3   =  137.8 W/m²
```

A real skin balance carries an evaporative term on the right-hand side as well.
Its absence is one reason the surface temperature computed here runs warmer than
a measured one — see section 7.


## 5. Exact solution

In each layer the equation is linear with constant coefficients:

```
ω_i > 0 :  θ_i(x) = A_i cosh(κ_i x) + B_i sinh(κ_i x) + q_met,i /(ω_i ρ_b c_b)
ω_i = 0 :  θ_i(x) = A_i + B_i x − q_met,i x² /(2 k_i)          with θ = T − T_a
```

**Method.** Take the state vector `s = [ θ ; k dθ/dx ]`. Those two components are
exactly the quantities that must be continuous at an interface, so the transfer
matrix of the stack is the ordered product of the layer matrices and no separate
interface equations are needed.

With the core Dirichlet condition fixed, the surface state is an **affine function
of the single unknown** `q_core = k dθ/dx` at `x = 0`. The radiative boundary
condition then closes the problem as one scalar nonlinear equation, solved by
Newton. **The only approximation in the reference is that scalar Newton tolerance,
which is driven to machine precision** — the residual reported is ~1e-14.

Reference implementation: `exact/db3_exact.py`. Values: `reference_values.json`.

### Self-consistency checks on the reference itself

Because the reference is derived here rather than cited, it is checked against
four independently known limits:

| Limit | Result |
|---|---|
| no perfusion, no radiation → series resistance `L/k + 1/h` | exact match |
| perfusion, adiabatic surface → `T ≡ T_a` | 0.0 |
| perfusion balanced by metabolism → `T ≡ T_a + q_met/(ω ρ_b c_b)` | 5.7e-14 |
| splitting one layer into two must change nothing | 0.0 |

## 6. Acceptance

By **observed order of convergence** on the shipped `h`, `h/2`, `h/4` meshes, not
by a fixed tolerance. Report the norm used — the expected order depends on it
(SPEC §4). Also report the energy balance and the radial variation, both of which
are threshold-free.

## 7. What this benchmark does NOT establish

* It does not show that the Pennes equation describes real tissue.
* The computed surface temperature at nominal perfusion is **309.45 K (36.3 °C)**,
  which is **higher than typical measured skin temperature** (about 32–34 °C in a
  24 °C room). That is expected: this is a self-consistent verification scenario,
  not a calibrated model of a forearm. If your code reproduces 309.45 K you have
  solved these equations correctly. You have not learned anything about skin.

---
---

# 한국어

## 1. 이 벤치마크가 무엇을 위한 것인가

솔버가 다음을 **한 문제 안에서 함께** 올바르게 다루는지 검증한다.

* **Pennes 관류 열싱크** `ω_b ρ_b c_b (T_a − T)` — 관류가 정확히 0 인 층 포함
* 전도도와 관류율이 다른 **다층 재료**
* **대류** 표면 경계조건
* **복사** 표면 경계조건 — 비선형이며 야코비안에 `4εσT³` 기여
* **축대칭 가중치** — 정확해에 반경 의존성이 없으므로, 계산된 장의 반경 변화는
  결함 신호다

**이것은 검증이지 확인이 아니다.** Pennes 식이 실제 피부를 기술하는지에 대해서는
아무것도 말하지 않는다. §7 참조.

## 2. 형상

반경 `R`, 두께 `L_tot` 의 원통이 축 방향으로 층을 이룬다. 측면은 단열이며,
축대칭 정식화에서 이는 자연 경계조건이라 아무 조치가 필요 없다.

```
  x = L_tot   ┌───────────────┐  표면 : 대류 + 복사
              │     표피      │  ω = 0  (무혈관)
              ├───────────────┤
              │     진피      │
              ├───────────────┤
              │   피하지방    │
  x = 0       └───────────────┘  심부 : Dirichlet T_core
              |<——— R ———>|        측면 : 단열
```

## 3. 물성과 그 출처

`【LIT】` 문헌에서 가져오고 출처를 기록한 값.
`【SCENARIO】` 본 벤치마크가 정하고 이유를 기록한 값.

**이 구분은 '구할 수 있었는가'가 아니라 '종류'의 구분이다.** 방사율·대류계수·환경
온도는 *상황*을 기술하므로 벤치마크 작성자가 정할 수 있다. 조직 물성은 *조직*을
기술하므로 작성자가 지어낼 수 없다.

| 항목 | 값 | 출처 |
|---|---|---|
| `k` 표피 / 진피 / 피하 | 0.21 / 0.37 / 0.16 W/(m·K) | `【LIT】` Parvin 외, *Engineering Reports* (Wiley, 2025) 3층 피부 모델 |
| 관류율, 표피 | **0** | `【LIT】` 표피는 혈관이 없으며, 피부 생체열 모델에서 표피에는 관류 항을 뺀다 |
| 관류율, 진피·피하 | 0.038 s⁻¹ | `【LIT】` 보고 범위 0–0.1 mL/mL/s, 0.038 채택 (*Sci. Rep.* 8, 2018) |
| `ρ_b c_b` | 1060 × 3770 = 3.9962e6 J/(m³·K) | `【LIT】` 혈액 밀도·비열, 동일 출처 |
| `q_met` | 368.1 W/m³ | `【LIT】` 동일 출처 |
| `T_core = T_a` | 310.15 K (37 °C) | `【LIT】` 혈액·심부 체온, 동일 출처 |
| 두께 비율 | 진피 ≈ 표피 × 12, 피하 ≈ 진피 × 3 | `【LIT】` 전완 안쪽 비율 (Electronics Cooling, 2023) |
| 두께 절대 규모 | 표피 0.1 mm → 총 4.9 mm | `【SCENARIO】` 비율은 문헌, 절대 규모는 부위마다 다르므로 하나를 골라야 한다 |
| `ε` | 0.98 | `【LIT】` Steketee (1973), *Spectral emissivity of skin and pericardium* — 1~14 µm 에서 측정한 **0.98 ± 0.01**, 파장과 색소 침착에 무관. 2009년 CO₂ 레이저 반사법 재측정 0.976 ± 0.006. 상온 물체가 복사하는 장파 적외선에서 성립하며, 3~5 µm 대역에서는 0.91~0.92 가 제안된다 |
| `h` | 5 W/(m²·K) | `【SCENARIO, 보고 범위 내】` 전신 자연대류 보고값 — 5.1 (Colin & Houdas 1967), 4.9/4.3 (Ichihara), 4.0 (Seppänen 1972), 3.4/3.3 (de Dear 1997), 3.3 (Omori 2004), 3.1 (Mitchell 1974). 부위별 범위 0.9~5.5. **5.0 은 범위 안이나 높은 쪽이다.** 대류와 복사가 비슷해지도록 고른 값 — 3a절 참조 |
| `T_∞ = T_env` | 297.15 K (24 °C) | `【SCENARIO】` 실내 조건. 한 숫자로 환경을 정의 |
| `R` | 5 mm | `【SCENARIO】` 임의 — 정확해가 여기에 의존하지 않는다 |

**피부 물성값은 연구 분야마다 상당히 다르다.** 위는 정합적인 *하나의* 조합이지
*그* 값이 아니다.

### 3a. 두 표면 계수에 관하여, 그리고 이 값들이 방어되는 이유

**선형화 복사계수.** 여기서 `4εσT_m³ = 6.20 W/(m²·K)` (`T_m = 303.3 K`) 인데,
실측 **전신** 복사계수는 약 4.5~4.7 W/(m²·K) 다. 모순이 아니다. 전신값은 유효 복사
면적 인자(약 0.7)를 포함한다. 팔다리가 방이 아니라 서로를 마주 보기 때문이다.
이 벤치마크는 **평평한** 표면을 낸 것이므로 그 인자가 1 이고, 명시된 형상에 대해
6.20 이 맞는 값이다.

**검증 벤치마크로서 이 계수들이 방어되는 이유.** 여기서 계수는 세 가지를 만족해야
하며, '실제 조직의 최선 추정치일 것' 은 그중에 없다.

| # | 요건 | 왜 |
|---|---|---|
| 1 | **고정되고 공개될 것** | 정확해가 이 값들의 함수다. 값이 흔들리면 참조값이 재현되지 않는다 |
| 2 | **물리적으로 허용될 것** — 부호, 자릿수, 보고된 범위 안 | 아니면 비물리적 영역에서 방정식을 푸는 것이고 검증에 의미가 없다 |
| 3 | **시험 대상 항을 실제로 시험하게 할 것** | `h` 가 크면 복사가 묻히고 `ω` 가 작으면 관류가 묻힌다. 여기서 `κL` = 3.51 / 0.77 / 0 이고 표면은 복사 55 % 대 대류 45 % 로 갈린다 |

참조값은 **측정이 아니라 명시된 방정식의 정확해**다. 어떤 계수를 넣든 정확해는 그
계수에 대해 정확하다. 따라서 계수의 현실성은 참조값의 정확성과 무관하며, 그것이
좌우하는 것은 **확인(validation)** 이고 이 모음은 확인을 주장하지 않는다
(7절, `DISCLAIMER.md` 3절).

**현실적인 조직 물성이 필요하면** 여기서 가져가지 말 것. IT'IS 데이터베이스를 쓰라 —
Baumgartner 외, *IT'IS Database for thermal and electromagnetic parameters of
biological tissues*, Version 5.0, 2025-08-21, DOI 10.13099/VIP21000-05-0,
`itis.swiss/database`. 값마다 평균·표준편차·범위·근거 논문 수를 제공하며, 일부
파라미터 특히 관류는 변동이 커서 시뮬레이션 결과에 심각한 영향을 줄 수 있다고
스스로 경고한다.

**추적하지 못한 것.** 층별 전도도, 관류율, 대사 발열, 혈액 열용량은 각각 위에 인용한
단일 2차 문헌에서 왔고, 그 1차 출처는 더 추적하지 못했다. 이는 벤치마크의 한계가
아니라 이 문서의 한계다. 벤치마크가 딛고 서는 것은 위 요건 1 이며, 값이
`exact/db3_properties.py` 에 고정되어 있고 `exact/run_reference.py` 가 재생성하므로
그 요건은 충족된다.

## 4. 지배방정식과 무차원 수

```
d/dx ( k_i dT/dx ) + ω_i ρ_b c_b ( T_a − T ) + q_met,i = 0        층 i 에서
κ_i = √( ω_i ρ_b c_b / k_i )
```

해는 층별 `κ_i L_i` 가 지배한다.

| 층 | 공칭 관류에서의 `κ_i L_i` |
|---|---|
| 피하지방 | 3.5072 |
| 진피 | 0.7688 |
| 표피 | 0 |

관류율을 배율로 조절해 세 영역을 훑는다.

| 경우 | 배율 | 피하 `κL` | 성격 |
|---|---|---|---|
| 약함 | ×0.1 | 1.109 | 전도 지배 |
| 공칭 | ×1 | 3.507 | 균형 |
| 강함 | ×10 | 11.09 | 심부 쪽에 얇은 열층 |

### 4a. 관류 항이 무엇이고 무엇이 아닌가

**대류가 아니다.** 이 벤치마크에도, 이것을 문제 그대로 푸는 어떤 코드에도 속도장이
없고 이류항 `v·∇T` 가 없다. Pennes 항은 혈액–조직 열교환을 **뭉뚱그린 대역**이다.
혈액이 `T_a` 로 들어와 국소 조직과 완전히 열평형에 이른 뒤 국소 온도로 나간다고
가정한다. **모델은 혈액이 어느 쪽으로 흐르는지 알지 못한다.**

따라서 조직 내부에서 **수송 기구는 전도뿐**이며, 관류는 그것에 열을 부어 넣는 분산
공급원이다. 세 기구는 서로 다른 장소에서 작용하므로 따로 비교해야 한다.

| 기구 | 어디서 | 어떻게 다루나 | 이 문제에서의 크기 |
|---|---|---|---|
| **혈류** | 조직 내부 | 체적 열원, **이류 없음** | **133.2 W/m² 공급** |
| **전도** | 조직 내부 | 정식으로 푼다 | **유일한 수송**: 심부 경계 2.8 → 표면 137.8 W/m² |
| **공기 대류** | 표면 | 경계조건 `h(T_s − T_∞)` | 61.5 W/m² (44.6 %) |
| **복사** | 표면 | 비선형 경계조건 | 76.3 W/m² (55.4 %) |
| 대사 | 조직 내부 | 체적 열원 | 1.8 W/m² (1.3 %) |

전도 유속이 적층을 지나며 50배로 커지는 것은 관류가 가는 길에 계속 열을 부어 넣기
때문이다. 관류가 0 인 표피에서는 전도 혼자 137.8 W/m² 를 전부 나른다.

두께 `L` 인 층에서 관류 대 전도의 세기:

| 층 | `κL` | `(κL)²` = 관류 / 전도 |
|---|---|---|
| 피하지방 | 3.507 | **12.30** — 관류 지배 |
| 진피 | 0.769 | 0.591 — 대등 |
| 표피 | 0 | 0 — 전도뿐 |

**표현되지 않은 것**: 이류항과 속도장, 대혈관, 동맥–정맥 역류 열교환, 온도 의존
관류 `ω(T)` — 따라서 가열이 혈류를 바꾸는 되먹임이 없다.

**출력 쪽에도 없는 것이 있다 — 증발이다.** 여기서 표면은 대류와 복사로만 열을
잃는다. 무감성 발한과 땀은 물질전달이며 열전달 벤치마크의 범위 밖이고, 호흡을 통한
손실은 애초에 피부 수지 밖이다. 이 문제에서 닫히는 수지는 다음과 같다.

```
혈류 133.2  +  대사 1.8  +  심부 전도 2.8
        =  대류 61.5  +  복사 76.3   =  137.8 W/m²
```

실제 피부의 수지에는 우변에 증발 항이 더 있다. 그것이 없다는 사실이, 여기서 계산된
표면 온도가 실측보다 따뜻하게 나오는 이유 중 하나다 — 7절 참조.


## 5. 정확해

각 층에서 방정식이 상수계수 선형이다.

```
ω_i > 0 :  θ_i(x) = A_i cosh(κ_i x) + B_i sinh(κ_i x) + q_met,i /(ω_i ρ_b c_b)
ω_i = 0 :  θ_i(x) = A_i + B_i x − q_met,i x² /(2 k_i)          θ = T − T_a
```

**방법.** 상태벡터를 `s = [ θ ; k dθ/dx ]` 로 잡는다. 이 두 성분이 바로 계면에서
연속이어야 하는 양이므로, 적층의 전달행렬이 층 행렬의 순서곱이 되고 **계면
방정식을 따로 쓸 필요가 없다.**

심부 Dirichlet 이 고정되므로 표면 상태는 **미지수 하나** `q_core = k dθ/dx |₀` 의
아핀 함수가 된다. 복사 경계조건이 이를 스칼라 비선형 방정식 하나로 닫고 Newton 으로
푼다. **참조해의 유일한 근사는 그 스칼라의 Newton 허용오차이며 기계 정밀도까지
낮춘다** — 보고된 잔차는 ~1e-14 이다.

참조 구현 `exact/db3_exact.py`, 값 `reference_values.json`.

### 참조해 자체의 자체 검증

참조해를 인용이 아니라 직접 유도했으므로, **독립적으로 알려진 극한 네 개**로
검증했다.

| 극한 | 결과 |
|---|---|
| 관류 0, 복사 0 → 직렬 저항 `L/k + 1/h` | 완전 일치 |
| 관류 有, 표면 단열 → `T ≡ T_a` | 0.0 |
| 관류와 대사가 평형 → `T ≡ T_a + q_met/(ω ρ_b c_b)` | 5.7e-14 |
| 한 층을 둘로 쪼개도 변하면 안 됨 | 0.0 |

## 6. 합격 판정

배포된 `h`, `h/2`, `h/4` 격자에서 **관측 수렴 차수**로 판정하며, 고정 허용오차를
쓰지 않는다. 사용한 노름을 반드시 밝힌다 — 기대 차수가 노름에 따라 다르다
(SPEC §4). 에너지 수지와 반경 변화도 함께 보고하며, 둘 다 임계값이 없다.

## 7. 이 벤치마크가 말해 주지 않는 것

* Pennes 식이 실제 조직을 기술한다는 것을 보이지 않는다.
* 공칭 관류에서 계산된 표면 온도는 **309.45 K (36.3 °C)** 로, **실측 피부 온도보다
  높다** (24 °C 실내에서 보통 32~34 °C). 이는 예상된 것이다. 이것은 자기정합적인
  검증 시나리오이지 전완을 보정한 모델이 아니다. **당신의 코드가 309.45 K 를
  재현하면 이 방정식들을 맞게 푼 것이다. 피부에 대해서 알게 된 것은 없다.**
