# Benchmark Problems / 벤치마크 문제 설명서

`yuchiri-axirad2D` v0.1.0 — problem definitions, drawings, exact answers, sources
문제 정의 · 도면 · 정답 · 출처

**Drawing / 도면** — `../figures/benchmark_definitions.png`
**Results / 결과** — `BENCHMARK_RESULTS.md`, `benchmark_comparison.csv`

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## 0. Principle behind the choice of these problems

Three requirements were imposed on every benchmark.

1. **2D axisymmetric.**
2. **Surface-to-surface radiation only** — no participating media, which the
   solver does not support.
3. **The reference must be an exact solution that we can compute ourselves from a
   published expression.** No numerical table from any publication is reproduced.

Requirement 3 is the strict one. Most published axisymmetric radiation benchmarks
are participating-media (RTE) problems, and most surface-to-surface references are
either tabulated numerical results or approximations. The three problems below
were chosen because in each case **the exact answer follows from a geometric fact
rather than from a fitted or tabulated number.**

| Benchmark | The geometric fact that makes it exact |
|---|---|
| BM-1 | A **convex** body **fully enclosed** by a cavity sees none of itself and all of the cavity: `F(1→1) = 0`, `F(1→2) = 1` |
| BM-2 | The view factor between **coaxial parallel disks** has a closed form |
| BM-5 | **Spherical symmetry** makes the irradiation of the outer sphere uniform, so the lumped two-surface formula becomes exact |

---

## 1. BM-1 — Coaxial cylindrical enclosure

### 1.1 Geometry

Axisymmetric, dimensions in metres.

| Region | r | z | Material |
|---|---|---|---|
| Inner body | 0 – 0.05 | 0.05 – 0.15 | solid, ε₁ = 0.8, **200 W** total generation |
| Cavity | 0 – 0.10 | 0.02 – 0.18 | vacuum (transparent) |
| Shell | 0 – 0.12 | 0.00 – 0.20 | solid, ε₂ = 1.0 (black) |

* Boundary: **Dirichlet 300 K** on r = 0.12, z = 0 and z = 0.20.
* Conductivity of both solids 5000 W/(m·K) — deliberately high so the surfaces are
  nearly isothermal and the analytic comparison is clean.
* Vacuum `k = 1e-5 W/(m·K)` (see the note in §4).
* Volumetric generation `q_vol = 200 / V_inner = 254 648 W/m³`.
* Rays 40 000, seed 12345.

### 1.2 Why the exact solution holds

The inner cylinder is **convex** and **entirely surrounded** by the cavity, so
every ray leaving it strikes the cavity wall and none returns directly:

```
F(1→1) = 0 ,   F(1→2) = 1            (from geometry alone)
```

With a **black** cavity wall (ε₂ = 1) at uniform temperature its radiosity is
σT₂⁴ and uniform, and because body 1 is convex every ray reflected from it also
goes to the wall. Hence

```
Q = ε₁ · A₁ · σ · (T₁⁴ − T₂⁴)                    exact, no approximation
```

`A₁ = 2πa·h + 2πa² = 0.0471238898 m²` with a = 0.05, h = 0.10.

### 1.3 Exact answers

| Quantity | Exact value |
|---|---|
| `F(1→1)` | 0 |
| `F(1→2)` | 1 |
| `A₁` | 0.0471238898 m² |
| `T₁` given T₂ = 300.0056 K and Q = 200 W | 564.6606 K |
| `Q` given the computed surface temperatures | 200.0000 W |

### 1.4 Computed and error

| Quantity | Computed | Error |
|---|---|---|
| `F(1→1)` | 0.0 | **exact** |
| `F(1→2)` | 1.000000000000 | **exact** |
| `A₁` | 0.0471238898 | **6.9e-18** |
| `T₁` | 564.6711 K | **+0.0019 %** |
| `Q` | 200.0162 W | **+0.0081 %** |

Leakage 0, closure exactly 1, normal mismatches 0, energy residual 1.11e-12,
Newton converged in 6 iterations.

---

## 2. BM-2 — Finite cylindrical enclosure

### 2.1 Geometry

| Region | r | z | Material |
|---|---|---|---|
| Cavity | 0 – 0.05 | 0.00 – 0.10 | vacuum (transparent) |
| Shell | 0 – 0.07 | −0.02 – 0.12 | solid, **ε = 1.0 (black)**, k = 30 W/(m·K) |

* Bottom shell (z < 0) carries **150 W** total generation.
* Boundary: Dirichlet 300 K on r = 0.07, z = −0.02, z = 0.12.
* Rays 60 000; the view-factor comparison uses **8 seeds**.

The cavity surface splits into three groups: **disk 1** (z = 0), **disk 2**
(z = L) and the **side wall** (r = R).

### 2.2 Why the exact solution holds

With **all** surfaces black there is no reflection, so a ray is absorbed at its
first strike and the Gebhart absorption factor equals the view factor:

```
ε = 1  ⇒  B_ab = F_ab
```

The code's Monte Carlo result can therefore be compared **directly** against the
closed-form view factor. This is what BM-1 could not do: there the view factors
were trivially 0 and 1.

### 2.3 Exact answers

Coaxial parallel disks of radii r₁, r₂ separated by L:

```
R₁ = r₁/L ,  R₂ = r₂/L ,  S = 1 + (1 + R₂²)/R₁²

F(1→2) = ½ { S − [ S² − 4 (r₂/r₁)² ]^½ }
```

For r₁ = r₂ = R = 0.05 and L = 0.10: R₁ = R₂ = 0.5, S = 6.

| Quantity | Exact value | Derivation |
|---|---|---|
| `F(disk1→disk2)` | **0.1715728753** | the expression above |
| `F(disk1→side)` | **0.8284271247** | `1 − F₁₂` (summation rule) |
| `F(side→disk1)` | **0.2071067812** | `A₁F₁ₛ/Aₛ` (reciprocity) |
| `F(side→side)` | **0.5857864376** | `1 − 2F(s→1)` |
| `F(disk1→disk1)` | **0** | the disk is planar |
| `A_disk` | 0.0078539816 m² | `πR²` |
| `A_side` | 0.0314159265 m² | `2πRL` |

### 2.4 Computed and error (8 seeds)

| Quantity | Computed mean | Exact | Error | Standard error |
|---|---|---|---|---|
| `F(disk1→disk2)` | 0.171501917 | 0.171572875 | **−0.0414 %** | 0.2636 % → **0.16 σ** |
| `F(side→disk1)` | 0.207167083 | 0.207106781 | **+0.0291 %** | 0.1828 % → **0.16 σ** |
| `F(disk1→disk1)` | 0.0 | 0 | **exact** | — |
| `A_disk`, `A_side` | — | — | **exact (diff 0)** | — |

Both deviations are **0.16 standard errors** — no evidence of systematic bias.

### 2.5 What BM-2 does not test

Because the shell surrounds the cavity, heat conducts around it rather than
crossing by radiation; the coupled run spans only 300 → 303 K. **BM-2 is a
radiation-geometry benchmark**; coupling is exercised by BM-1 and BM-5.

---

## 3. BM-5 — Concentric spheres

### 3.1 Geometry

Mapped from (ρ, θ) with `r = ρ sin θ`, `z = ρ cos θ`, θ ∈ [0, π].

| Region | ρ | Material |
|---|---|---|
| Inner shell | 0.02 – 0.04 | solid, ε₁ = 0.8, **300 W** total generation |
| Cavity | 0.04 – 0.08 | vacuum (transparent) |
| Outer shell | 0.08 – 0.10 | solid, ε₂ = 0.5 |

* `ρ < 0.02` is **not meshed** — elements would degenerate at the centre and fail
  the G1 Jacobian check. That surface is the outer face of an opaque solid and is
  therefore not extracted as a radiating surface. Physically it is simply a hollow
  spherical shell, which does not affect the radiative exchange.
* Boundary: **Dirichlet 300 K** on ρ = 0.10.
* Conductivity of both solids 400 W/(m·K). Rays 40 000, seed 21.

### 3.2 Why the exact solution holds — and why this problem matters

For **concentric spheres** the whole system is rotationally symmetric about any
axis through the centre, so **the irradiation of the inner face of the outer
sphere is uniform.** The uniform-radiosity assumption built into the lumped
two-surface formula is therefore satisfied, and the formula is exact:

```
Q = σ (T₁⁴ − T₂⁴) / [ 1/(ε₁A₁) + (1/ε₂ − 1)/A₂ ]
A₁ = 4πa² ,  A₂ = 4πb²
```

**This benchmark tests an earlier interpretation as well as the code.** In BM-1
the same lumped formula deviated by about 1.6 % with a gray wall, and the
deviation did not shrink with more rays. The explanation offered was that the
cylindrical cavity wall is irradiated non-uniformly. If that explanation is
correct, the formula must agree in concentric spheres. If it disagreed here, the
explanation would be wrong and the code would be suspect.

### 3.3 Exact answers

| Quantity | Exact value |
|---|---|
| `A₁` (true sphere) | 0.0201061930 m² |
| `A₂` (true sphere) | 0.0804247719 m² |
| Resistance `R` | 74.603880 (SI) |
| `Q` at T₁ = 1000 K, T₂ = 300 K | 753.9078 W |
| `F(1→1)` (black limit) | 0 |
| `F(1→2)` (black limit) | 1 |

**Faceting correction.** The segments are straight conical frusta, so the meshed
surface area is slightly below the true sphere. The `Q` comparison therefore uses
the **code's own computed areas** in the exact expression, which separates
geometric discretisation from radiation-algorithm error.

### 3.4 Computed and error

**Faceting convergence** (Δθ², the theoretical order for a chord approximating an arc)

| nθ | Segments | `A₁` error | Ratio |
|---|---|---|---|
| 12 | 24 | −0.8555 % | — |
| 24 | 48 | −0.2141 % | **4.00** |
| 48 | 96 | −0.0535 % | **4.00** |

**Black limit** — `F(1→1) = 0.000e+00` (exact), `F(1→2) = 1.000000000000` (exact).
Convexity survives the polyhedral approximation.

> For gray surfaces `B(1→1) ≠ 0`. Rays reflected from the outer sphere return to
> the inner one; this is correct. `F(1→1) = 0` equals `B(1→1) = 0` only for black
> surfaces.

**Gray isothermal exchange** (ε₁ = 0.8, ε₂ = 0.5, 1000 K / 300 K)

| Reference | Value | Error |
|---|---|---|
| `Q_code` | 752.0272 W | — |
| exact, using the code's areas | 752.2936 W | **−0.0354 %** |
| exact, using true sphere areas | 753.9078 W | −0.2494 % (includes faceting) |

**Coupled solve** (300 W generation, outer wall 300 K)

```
T ∈ [300.00, 797.65] K      T₁ = 797.1519 K   T₂ = 300.1983 K
Q (exact, at computed temperatures and areas) = 300.0959 W  vs input 300 W  → +0.0320 %
Energy residual 5.684e-14 ; Newton converged in 9 iterations
```

**Verdict on the earlier interpretation** — the gray lumped formula agrees to
−0.035 % here, against −1.6 % in the cylindrical cavity. **The BM-1 deviation
comes from the formula's assumption, not from a code defect.**

---

## 4. Modelling notes common to all three

* **Transparent regions are given `k = 1e-5 W/(m·K)`, not zero.** With `k = 0` the
  equations for interior nodes of that region are singular. The parasitic
  conduction is of order 0.005 % of the heat flow. **Temperatures plotted inside
  the transparent region have no physical meaning.**
* **Solid conductivities are set high on purpose** in BM-1 and BM-5 so that the
  radiating surfaces are nearly isothermal. This isolates the radiation model from
  conduction-side discretisation error. It is a benchmark design choice, not a
  physical claim.
* **Total power is a computed result, not an input.** `q_vol` is prescribed per
  element and `P = Σ q_vol · V_e` is reported. In BM-5 the reported input is
  299.999725 W rather than 300 W because the faceted mesh volume is slightly below
  the true spherical shell while `q_vol` was derived from the true volume.

## 5. Sources

**All numbers in this document were computed by us**, from the expressions given
above. No numerical table from any publication is reproduced. Mathematical
expressions are not themselves subject to copyright; they are restated here so
that the document is self-contained and independently checkable.

| Result used | Where such expressions are compiled |
|---|---|
| Coaxial parallel disks view factor | J. R. Howell, *A Catalog of Radiation Heat Transfer Configuration Factors* — freely available at `thermalradiation.net`. Also in standard texts (Modest, *Radiative Heat Transfer*; Siegel & Howell, *Thermal Radiation Heat Transfer*; Incropera et al.) |
| Two-surface enclosure, convex body fully enclosed | Standard textbook result; the same texts |
| Concentric spheres exchange | Standard textbook result; the same texts |
| Free compilation of axisymmetric view factors | I. Martínez, *Radiative view factors*, Universidad Politécnica de Madrid — freely available PDF |

**Honest limitation.** In preparing this document the primary sources were
identified but their **full texts were not opened**; the expressions used are the
standard ones and were verified by internal consistency instead — the summation
rule (`ΣF = 1`), reciprocity (`A_aF_ab = A_bF_ba`), and the black-limit identities
`F(1→1) = 0`, `F(1→2) = 1` all hold to the precision reported above. Readers who
need a citable primary reference should consult the compilations listed.

**Related but not used.** For an open spherical cavity with an aperture an exact
apparent-emissivity expression exists (F. E. Nicodemus, *Applied Optics*, 1968,
derived without geometric approximation). That case is a candidate for a future
benchmark; it is **not** used here because modelling the aperture as a 0 K black
surface has not been validated in this code.

---
---

# 한국어

## 0. 이 문제들을 고른 원칙

모든 벤치마크에 세 가지 요건을 걸었다.

1. **2차원 축대칭일 것.**
2. **표면 대 표면 복사만 있을 것** — 참여 매질은 본 솔버가 지원하지 않는다.
3. **참조값이 공개된 수식으로 우리가 직접 계산할 수 있는 정확해일 것.**
   어떤 문헌의 수치표도 복제하지 않는다.

요건 3이 까다롭다. 문헌의 축대칭 복사 벤치마크는 대부분 참여 매질(RTE) 문제이고,
표면 대 표면 참조값은 대부분 수치표이거나 근사식이다. 아래 세 문제를 고른 이유는,
각각 **정확해가 맞춘 값이나 표가 아니라 기하학적 사실에서 나오기 때문**이다.

| 벤치마크 | 정확해가 성립하는 기하학적 사실 |
|---|---|
| BM-1 | **볼록**체가 공동에 **완전히 포위**되면 자기 자신을 보지 못하고 공동만 본다: `F(1→1) = 0`, `F(1→2) = 1` |
| BM-2 | **동축 평행 원판**의 형상계수에 닫힌 형태가 있다 |
| BM-5 | **구대칭**이면 바깥 구의 조사량이 균일하므로 2면 집중식이 정확해진다 |

---

## 1. BM-1 — 동축 원통 밀폐공동

### 1.1 형상

축대칭, 단위 m.

| 영역 | r | z | 재료 |
|---|---|---|---|
| 내부물체 | 0 – 0.05 | 0.05 – 0.15 | 고체, ε₁ = 0.8, **총 200 W** 발열 |
| 공동 | 0 – 0.10 | 0.02 – 0.18 | 진공 (투명) |
| 껍질 | 0 – 0.12 | 0.00 – 0.20 | 고체, ε₂ = 1.0 (흑체) |

* 경계: r = 0.12, z = 0, z = 0.20 에 **Dirichlet 300 K**
* 두 고체의 전도도 5000 W/(m·K) — **일부러 크게** 두어 표면을 거의 등온으로 만들고
  해석해 대조를 깨끗하게 한다
* 진공 `k = 1e-5 W/(m·K)` (§4 참조)
* 체적 발열률 `q_vol = 200 / V_내부 = 254 648 W/m³`
* 광선 40 000, 씨앗 12345

### 1.2 정확해가 성립하는 이유

내부 원통이 **볼록**하고 공동에 **완전히 둘러싸여** 있으므로, 여기서 나간 광선은
전부 공동벽에 닿고 자기 자신으로 직접 돌아오지 않는다.

```
F(1→1) = 0 ,   F(1→2) = 1            (기하만으로 성립)
```

공동벽이 **흑체**(ε₂ = 1)이고 등온이면 그 복사도는 σT₂⁴ 로 균일하며, 물체 1 이
볼록하므로 1 에서 반사된 광선도 반드시 벽으로 간다. 따라서

```
Q = ε₁ · A₁ · σ · (T₁⁴ − T₂⁴)                    정확. 근사 없음
```

a = 0.05, h = 0.10 에서 `A₁ = 2πa·h + 2πa² = 0.0471238898 m²`.

### 1.3 정답

| 항목 | 정확값 |
|---|---|
| `F(1→1)` | 0 |
| `F(1→2)` | 1 |
| `A₁` | 0.0471238898 m² |
| `T₁` (T₂ = 300.0056 K, Q = 200 W 일 때) | 564.6606 K |
| `Q` (계산된 표면온도에서) | 200.0000 W |

### 1.4 계산값과 오차

| 항목 | 계산값 | 오차 |
|---|---|---|
| `F(1→1)` | 0.0 | **정확** |
| `F(1→2)` | 1.000000000000 | **정확** |
| `A₁` | 0.0471238898 | **6.9e-18** |
| `T₁` | 564.6711 K | **+0.0019 %** |
| `Q` | 200.0162 W | **+0.0081 %** |

누출 0, 폐쇄성 정확히 1, 법선 불일치 0, 에너지 잔차 1.11e-12, Newton 6회 수렴.

---

## 2. BM-2 — 유한 원통 밀폐공동

### 2.1 형상

| 영역 | r | z | 재료 |
|---|---|---|---|
| 공동 | 0 – 0.05 | 0.00 – 0.10 | 진공 (투명) |
| 껍질 | 0 – 0.07 | −0.02 – 0.12 | 고체, **ε = 1.0 (흑체)**, k = 30 W/(m·K) |

* 아래 껍질(z < 0)에 **총 150 W** 발열
* 경계: r = 0.07, z = −0.02, z = 0.12 에 Dirichlet 300 K
* 광선 60 000. 형상계수 대조는 **씨앗 8개** 평균

공동면은 세 무리로 나뉜다 — **원판 1**(z = 0), **원판 2**(z = L), **측벽**(r = R).

### 2.2 정확해가 성립하는 이유

**전 면이 흑체**이면 반사가 없어 광선이 첫 충돌에서 흡수되므로, Gebhart 흡수계수가
형상계수와 같아진다.

```
ε = 1  ⇒  B_ab = F_ab
```

따라서 코드의 몬테카를로 결과를 닫힌 형태 형상계수와 **직접** 대조할 수 있다.
BM-1 에서는 형상계수가 0 과 1 뿐이라 할 수 없던 일이다.

### 2.3 정답

반경 r₁, r₂, 간격 L 인 동축 평행 원판:

```
R₁ = r₁/L ,  R₂ = r₂/L ,  S = 1 + (1 + R₂²)/R₁²

F(1→2) = ½ { S − [ S² − 4 (r₂/r₁)² ]^½ }
```

r₁ = r₂ = R = 0.05, L = 0.10 이면 R₁ = R₂ = 0.5, S = 6.

| 항목 | 정확값 | 유도 |
|---|---|---|
| `F(원판1→원판2)` | **0.1715728753** | 위 식 |
| `F(원판1→측벽)` | **0.8284271247** | `1 − F₁₂` (합의 법칙) |
| `F(측벽→원판1)` | **0.2071067812** | `A₁F₁ₛ/Aₛ` (상반성) |
| `F(측벽→측벽)` | **0.5857864376** | `1 − 2F(s→1)` |
| `F(원판1→원판1)` | **0** | 원판은 평면 |
| `A_원판` | 0.0078539816 m² | `πR²` |
| `A_측벽` | 0.0314159265 m² | `2πRL` |

### 2.4 계산값과 오차 (씨앗 8개)

| 항목 | 계산 평균 | 정확해 | 오차 | 표준오차 |
|---|---|---|---|---|
| `F(원판1→원판2)` | 0.171501917 | 0.171572875 | **−0.0414 %** | 0.2636 % → **0.16 σ** |
| `F(측벽→원판1)` | 0.207167083 | 0.207106781 | **+0.0291 %** | 0.1828 % → **0.16 σ** |
| `F(원판1→원판1)` | 0.0 | 0 | **정확** | — |
| `A_원판`, `A_측벽` | — | — | **정확 (차 0)** | — |

두 편차 모두 **표준오차의 0.16배** — 계통 편차의 증거가 없다.

### 2.5 BM-2 가 시험하지 않는 것

껍질이 공동을 둘러싸고 있어 열이 복사로 건너기보다 껍질을 통해 돌아 나간다.
결합 해석의 온도 범위는 300 → 303 K 에 그친다. **BM-2 는 복사 기하 벤치마크**이며,
결합 검증은 BM-1 과 BM-5 가 담당한다.

---

## 3. BM-5 — 동심 구

### 3.1 형상

`r = ρ sin θ`, `z = ρ cos θ`, θ ∈ [0, π] 로 사상한다.

| 영역 | ρ | 재료 |
|---|---|---|
| 내부 껍질 | 0.02 – 0.04 | 고체, ε₁ = 0.8, **총 300 W** 발열 |
| 공동 | 0.04 – 0.08 | 진공 (투명) |
| 외부 껍질 | 0.08 – 0.10 | 고체, ε₂ = 0.5 |

* `ρ < 0.02` 는 **격자로 만들지 않는다** — 중심에서 요소가 퇴화해 G1 야코비안 검사에
  걸린다. 그 면은 불투명체의 외곽면이므로 복사면으로 추출되지 않는다. 물리적으로는
  속이 빈 구각(球殼)일 뿐이며 복사 교환에 영향이 없다.
* 경계: ρ = 0.10 에 **Dirichlet 300 K**
* 두 고체의 전도도 400 W/(m·K). 광선 40 000, 씨앗 21

### 3.2 정확해가 성립하는 이유 — 그리고 이 문제가 중요한 이유

**동심 구**는 중심을 지나는 어떤 축에 대해서도 회전 대칭이므로, **바깥 구 내면의
조사량이 균일**하다. 2면 집중식이 전제하는 복사도 균일 가정이 실제로 성립하고,
따라서 그 식이 정확해진다.

```
Q = σ (T₁⁴ − T₂⁴) / [ 1/(ε₁A₁) + (1/ε₂ − 1)/A₂ ]
A₁ = 4πa² ,  A₂ = 4πb²
```

**이 벤치마크는 코드뿐 아니라 앞선 해석도 검증한다.** BM-1 에서 회색벽일 때 같은
집중식이 약 1.6 % 어긋났고 광선을 늘려도 줄지 않았다. 그때 제시된 설명은 "원통
공동벽은 조사량이 균일하지 않다"였다. 그 설명이 옳다면 동심 구에서는 일치해야 한다.
여기서도 어긋난다면 그 설명이 틀렸고 코드를 의심해야 한다.

### 3.3 정답

| 항목 | 정확값 |
|---|---|
| `A₁` (참 구면) | 0.0201061930 m² |
| `A₂` (참 구면) | 0.0804247719 m² |
| 저항 `R` | 74.603880 (SI) |
| `Q` (T₁ = 1000 K, T₂ = 300 K) | 753.9078 W |
| `F(1→1)` (흑체 한계) | 0 |
| `F(1→2)` (흑체 한계) | 1 |

**다면체 근사 보정.** 세그먼트가 직선 원뿔대이므로 격자 표면적이 참 구면보다 약간
작다. 따라서 `Q` 대조는 **코드가 계산한 면적**을 정확해 식에 넣어 수행한다. 그러면
형상 이산화 오차와 복사 알고리즘 오차가 분리된다.

### 3.4 계산값과 오차

**곡면 근사 수렴** (Δθ² — 현이 원호를 근사할 때의 이론 차수)

| nθ | 세그먼트 | `A₁` 오차 | 감소비 |
|---|---|---|---|
| 12 | 24 | −0.8555 % | — |
| 24 | 48 | −0.2141 % | **4.00** |
| 48 | 96 | −0.0535 % | **4.00** |

**흑체 한계** — `F(1→1) = 0.000e+00` (정확), `F(1→2) = 1.000000000000` (정확).
다면체 근사에서도 볼록성이 유지된다.

> 회색면에서는 `B(1→1) ≠ 0` 이다. 바깥 구에서 반사되어 돌아온 광선이 잡히기
> 때문이며 정상이다. `F(1→1) = 0` 은 흑체일 때만 `B(1→1) = 0` 과 같다.

**회색 등온 교환** (ε₁ = 0.8, ε₂ = 0.5, 1000 K / 300 K)

| 기준 | 값 | 오차 |
|---|---|---|
| `Q_code` | 752.0272 W | — |
| 정확해 (코드 계산 면적) | 752.2936 W | **−0.0354 %** |
| 정확해 (참 구면 면적) | 753.9078 W | −0.2494 % (면적 이산화 포함) |

**결합 해석** (300 W 발열, 외벽 300 K)

```
T ∈ [300.00, 797.65] K      T₁ = 797.1519 K   T₂ = 300.1983 K
Q(정확해, 계산 온도·면적) = 300.0959 W   투입 300 W   → +0.0320 %
에너지 잔차 5.684e-14 ; Newton 9회 수렴
```

**앞선 해석에 대한 판정** — 여기서는 회색 집중식이 −0.035 % 로 일치했고, 원통
공동에서는 −1.6 % 였다. **BM-1 의 편차는 집중식의 가정 때문이지 코드 결함이 아니다.**

---

## 4. 세 문제에 공통인 모델링 주의

* **투명 영역에 `k = 1e-5 W/(m·K)` 를 준다. 0 이 아니다.** `k = 0` 이면 그 영역
  내부 절점의 방정식이 특이해진다. 기생 전도는 열유동의 0.005 % 수준이다.
  **투명 영역 내부에 그려지는 온도는 물리적 의미가 없다.**
* **BM-1 과 BM-5 는 고체 전도도를 일부러 크게 두었다.** 복사면을 거의 등온으로
  만들어 복사 모델을 전도 쪽 이산화 오차로부터 분리하기 위해서다. 이는 벤치마크
  설계상의 선택이지 물리적 주장이 아니다.
* **총 전력은 입력이 아니라 계산 결과다.** 요소별 `q_vol` 을 주고
  `P = Σ q_vol · V_e` 를 보고한다. BM-5 의 보고값이 300 W 가 아니라 299.999725 W
  인 것은, `q_vol` 을 참 부피로 계산했는데 다면체 격자의 부피가 약간 작기 때문이다.

## 5. 출처

**이 문서의 모든 수치는 위 수식으로 우리가 직접 계산했다.** 어떤 문헌의 수치표도
복제하지 않았다. 수식 자체는 저작권 대상이 아니며, 문서가 자립적이고 독립 검증
가능하도록 여기에 다시 적었다.

| 사용한 결과 | 그런 수식이 정리되어 있는 곳 |
|---|---|
| 동축 평행 원판 형상계수 | J. R. Howell, *A Catalog of Radiation Heat Transfer Configuration Factors* — `thermalradiation.net` 에서 무료로 공개. 표준 교과서에도 있다 (Modest, *Radiative Heat Transfer*; Siegel & Howell, *Thermal Radiation Heat Transfer*; Incropera 외) |
| 2면 밀폐공간, 볼록체 완전 포위 | 표준 교과서 결과. 위와 같은 문헌 |
| 동심 구 교환 | 표준 교과서 결과. 위와 같은 문헌 |
| 축대칭 형상계수 무료 정리 | I. Martínez, *Radiative view factors*, 마드리드 공과대학 — 무료 PDF |

**정직하게 밝히는 한계.** 이 문서를 준비하면서 위 1차 출처를 **식별하기는 했으나
전문을 열람하지는 않았다.** 사용한 수식은 표준적인 것이며, 대신 **내적 정합성으로
검증**했다 — 합의 법칙(`ΣF = 1`), 상반성(`A_aF_ab = A_bF_ba`), 흑체 한계의
`F(1→1) = 0`·`F(1→2) = 1` 이 모두 위에 보고한 정밀도로 성립한다. 인용 가능한 1차
문헌이 필요한 독자는 위 정리 문헌을 참조하시기 바란다.

**관련되나 사용하지 않은 것.** 개구가 있는 구형 공동의 겉보기 방사율에는 정확한
닫힌 형태가 존재한다 (F. E. Nicodemus, *Applied Optics*, 1968 — 기하학적 근사 없이
유도). 장래 벤치마크 후보이나, 개구를 0 K 흑체 면으로 모델링하는 방식이 본 코드에서
검증되지 않았으므로 **여기서는 사용하지 않았다.**
