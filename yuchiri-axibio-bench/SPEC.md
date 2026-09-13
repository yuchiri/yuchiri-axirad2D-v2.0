# Axisymmetric Bioheat Verification Benchmark Suite — Specification v0.1
# 축대칭 생체열전달 검증 벤치마크 모음 — 사양서 v0.1

**Status / 성격** DRAFT for the author's approval. Nothing has been implemented.
**초안. 작성자 승인 대기. 아직 아무것도 구현하지 않았다.**

**Intended visibility / 공개 방침** **This specification is public.**
Unlike the `yuchiri-axirad2D` specification — which was a private design record —
this document *is* the product. A benchmark that no one can read is not a benchmark.
**이 사양서는 공개한다.** 설계 기록이었던 이전 사양서와 달리, 이 문서 자체가
산출물이다. 읽을 수 없는 벤치마크는 벤치마크가 아니다.

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## §0 Notation

| Mark | Meaning |
|---|---|
| `【FACT】` | Physical law, mathematical definition, or a decision already fixed by the author |
| `【DESIGN】` | A choice this document makes. Another choice was possible |
| `【JUDGEMENT】` | Opinion or estimate. Not a fact |
| `【OPEN】` | Not decided. Collected in §9 |
| `【IMPLEMENTER】` | This document deliberately does not decide it |
| `**` | Uncertain or weakly grounded statement |

## §1 Purpose and non-purpose

### 1.1 What this suite is

`【FACT】` A set of **verification** problems for axisymmetric bioheat solvers, in
which the reference is an **exact solution derived in this document**, not a
tabulated number and not the output of another code.

`【FACT】` It is **code-independent**. Any solver that can impose the stated
geometry, properties and boundary conditions can run it.

### 1.2 What this suite is NOT — read this first

`【FACT】` **This is verification, not validation.** In the sense of ASME V&V 40:

| | Question answered | Available here |
|---|---|---|
| **Verification** | Does the code solve the equations correctly? | **Yes** |
| **Validation** | Do those equations describe real tissue? | **No** |

`【FACT】` **The Pennes equation is itself a modelling hypothesis, not a law.**
Measured tissue temperature profiles have been reported to agree with effective-
conductivity models and not with the conventional heat-sink picture. Passing every
benchmark in this suite says nothing about whether Pennes describes your tissue.

`【JUDGEMENT】` This limit is not a weakness of the suite; it is the reason the
suite is worth having. In a field where validation is hard — you cannot measure
the field inside a living system — verification is the part that *can* be made
airtight, and it should be.

`【FACT】` Also outside scope: participating-media radiation (tissue optics),
anisotropic conductivity, large-vessel counter-current models, phase change
(cryoablation), electromagnetics (SAR is taken as a prescribed source, never solved).

## §2 Governing equation

`【FACT】` Steady Pennes bioheat equation, axisymmetric:

```
∇·( k(T) ∇T )  +  ω_b ρ_b c_b ( T_a − T )  +  q_met  +  q_ext  =  0
dV = 2π r dr dz
```

| Symbol | Meaning | Unit |
|---|---|---|
| `k` | tissue thermal conductivity | W/(m·K) |
| `ω_b` | blood perfusion rate | 1/s (volumetric, per unit tissue volume) |
| `ρ_b c_b` | blood volumetric heat capacity | J/(m³·K) |
| `T_a` | arterial (blood) temperature | K |
| `q_met` | metabolic heat generation | W/m³ |
| `q_ext` | external heat source (SAR, RF, laser, magnetic) | W/m³ |

`【DESIGN】` Define `θ = T − T_a` and the **perfusion length scale**

```
κ = √( ω_b ρ_b c_b / k )        [1/m]        L_p = 1/κ
```

`【FACT】` With constant properties the homogeneous equation becomes `∇²θ = κ²θ`.
**Every exact solution in this suite follows from that one line.**

`【DESIGN】` Transient problems are **not** included in v0.1. See `【OPEN】` M-6.

## §3 What a benchmark entry must contain

`【DESIGN】` Each entry ships five things. An entry missing any of them is not
admitted to the suite.

| # | Item | Why |
|---|---|---|
| 1 | **Problem definition** — geometry, properties, boundary conditions, in SI, with no free parameters | So two people build the same problem |
| 2 | **Derivation of the exact solution** — written out, not cited | So a reader can check it without a library |
| 3 | **Reference implementation** — a short script computing the exact solution | So the number is reproducible, not transcribed |
| 4 | **Acceptance criterion** — see §4 | So "passing" is not a matter of taste |
| 5 | **Report schema** — see §5 | So results from different codes are comparable |

`【FACT】` **No numerical table from any publication is reproduced anywhere in this
suite.** Every reference number is computed by item 3 from the expression in item 2.

## §4 Acceptance criterion — order, not tolerance

`【DESIGN】` **A benchmark is passed by demonstrating the expected order of
convergence under mesh refinement, not by meeting a fixed error threshold.**

`【JUDGEMENT】` The reason is the one this author has applied throughout: a fixed
tolerance is an unjustified constant. It depends on the mesh, the element order and
the problem scale, none of which the suite controls. An observed convergence order
does not.

`【DESIGN】` Required report per benchmark:

```
for at least three successive refinements h, h/2, h/4:
    e(h) = || T_computed − T_exact ||          (norm declared by the runner)
    observed order  p = log2( e(h) / e(h/2) )
```

**The expected order depends on WHAT is measured.** This was stated too loosely
in the first draft and is corrected here.

| Measured quantity | Linear elements | Quadratic elements |
|---|---|---|
| **Nodal values, L∞** | 2 | **4** — nodal superconvergence in 1D |
| Field, L2 | 2 | 3 |
| Gradient / flux | 1 | 2 |

`【FACT】` Correction record. The v0.1 draft gave "quadratic → 3" without naming
the norm. Measured on DB-3, the observed order of the **nodal L∞ error** was
**3.81 → 3.90** (nominal perfusion), **3.95 → 3.97** (weak) and **3.67 → 3.83**
(strong). These are consistent with 4, not with 3. In one dimension the nodal
values of a finite element solution converge faster than the field between the
nodes; for order-`p` elements this is `O(h^{2p})`. The table above now says so.

`【JUDGEMENT】` The correction does not change any pass/fail outcome, because the
hard failure condition proposed below is `p < 1`. But a benchmark that states
the wrong expectation trains its users to accept the wrong thing.

`【OPEN】` M-2 — the width of the "declared band". Setting it is exactly the kind of
unjustified constant this project avoids. Candidate: report `p` and let the reader
judge, with a hard failure only when `p < 1` (i.e. not converging at all), which is
what caught the transposed-Jacobian defect in `yuchiri-axirad2D`.

`【DESIGN】` **In addition**, every entry reports two threshold-free quantities:

* the **global energy balance residual** — heat generated plus heat entering equals
  heat leaving, to round-off;
* the **limit check** — as `κ → 0` the solution must reduce to the pure-conduction
  solution of the same geometry, which is separately known.

## §5 Report schema

`【DESIGN】` One JSON file per (code, benchmark, mesh) triple.

```
{ "suite_version", "benchmark_id", "code_name", "code_version",
  "element_type", "n_nodes", "n_elements", "characteristic_h",
  "error_Linf", "error_L2", "observed_order",
  "energy_residual_relative",
  "dimensionless_groups",         // the groups that govern the case, see §6
  // error_L2 is optional; whichever norm is used must be named in "norm"
  "notes" }
```

`【IMPLEMENTER】` File layout, tooling and language of the runner.

## §6 Dimensionless grouping

`【FACT】` For constant properties, the geometry-plus-perfusion problem depends on
**one dimensionless group per length scale**:

```
DB-1, DB-2 :  κa        (perfusion length vs applicator radius)
              b/a       (outer radius vs applicator radius)
DB-3       :  κ_i L_i   per layer
```

`【DESIGN】` Each benchmark is run at **three values of `κa` spanning the regimes**:

| Regime | `κa` | Physical meaning |
|---|---|---|
| conduction-dominated | 0.1 | perfusion barely matters — should approach pure conduction |
| balanced | 1 | the interesting case |
| perfusion-dominated | 10 | sharp thermal boundary layer near the source |

`【JUDGEMENT】` The `κa = 10` case is the demanding one: it creates a thin layer
that a coarse mesh will smear. **A code that passes only at `κa = 0.1` has not been
tested.**

---

## §7 The three benchmarks

### DB-1 — Spherical surface source in perfused tissue

**Physical setting.** Magnetic-fluid hyperthermia: a shell of magnetic nanoparticles
on the surface of a spherical tumour, delivering total power `P`.

**Geometry.** Spherical shell `a ≤ r ≤ b`, axisymmetric (a sphere is a body of
revolution). Inner surface `r = a` carries a prescribed inward flux totalling `P`.
Outer surface `r = b` is Dirichlet at `T_a`.

`【DESIGN】` The region `r < a_0 < a` is not meshed, to avoid element degeneration at
the centre — the same device used in `yuchiri-axirad2D` BM-5.

**Exact solution.** With `θ = T − T_a`:

```
(1/r²)(r² θ′)′ = κ² θ        ⇒    θ(r) = A e^(−κr)/r  +  B e^(+κr)/r
```

`A, B` follow in closed form from `θ(b) = 0` and `P = 4πa²·(−k θ′(a))`.

In the unbounded limit `b → ∞` (`B = 0`):

```
θ(r) = P · e^(−κ(r−a)) / [ 4π k r (1 + κa) ]
θ(a) = P / [ 4π k a (1 + κa) ]
```

`【FACT】` Sanity limit: as `κ → 0`, `θ(r) → P/(4πkr)`, the classical point-source
conduction solution. This is the `κ → 0` limit check of §4.

**What it verifies.** The perfusion term itself; spherical mapping; surface flux
boundary condition; the `κ → 0` reduction.

**Reuse.** `【JUDGEMENT】` The polar mesh generator, the axis-snapping fix and the
verification script of `yuchiri-axirad2D` BM-5 transfer almost unchanged. **This is
the cheapest of the three and should be first.**

---

### DB-2 — Cylindrical applicator in perfused tissue

**Physical setting.** A radiofrequency, microwave or laser ablation probe of radius
`a` inserted into tissue.

**Geometry.** Annulus `a ≤ r ≤ b`, axial extent `L` with **adiabatic ends**, so the
solution is a function of `r` only. Prescribed inward flux at `r = a` totalling `P`
per unit length; Dirichlet `T_a` at `r = b`.

**Exact solution.**

```
(1/r)(r θ′)′ = κ² θ        ⇒    θ(r) = A K₀(κr) + B I₀(κr)
θ′(r) = κ [ −A K₁(κr) + B I₁(κr) ]
```

`A, B` from `θ(b) = 0` and `P′ = 2πa·(−k θ′(a))`, where `P′` is power per unit axial
length. `K₀, K₁, I₀, I₁` are modified Bessel functions, evaluated by the reference
implementation.

`【FACT】` Sanity limit: as `κ → 0`, `θ(r) → (P′/2πk)·ln(b/r)`, the classical
cylindrical conduction solution — the same `ln r` profile already used as a
verification case in `yuchiri-axirad2D`.

**What it verifies.** `【JUDGEMENT】` The **non-trivial special-function reference**.
This is to DB-2 what the closed-form view factor was to BM-2 in the previous
project: the first benchmark whose exact answer is neither 0, 1 nor an exponential.
It also exercises the interaction of the `2πr` axisymmetric weight with the
perfusion term — two things that must both be right for the answer to come out.

**Trap to avoid.** `【JUDGEMENT】` The adiabatic-end idealisation is exact only if
the ends really are adiabatic. If a code silently applies something else there, the
error will look like a discretisation error. **The report must state the axial
boundary condition explicitly.**

---

### DB-3 — Layered skin with perfusion and radiative surface loss

**Physical setting.** Skin exposed to a room: three layers (epidermis, dermis,
subcutaneous fat) with different conductivity and perfusion, losing heat from the
surface by **convection and radiation**.

**Geometry.** A cylinder of radius `R` and thickness `L`, with the **lateral surface
adiabatic**, so the exact solution depends on the axial coordinate only.
`【JUDGEMENT】` This has a second purpose: a correct axisymmetric code must produce a
field with **no r-dependence at all**. Any radial variation is a defect signal.

**Boundary conditions.**

```
x = 0   (core side)     T = T_core                     (Dirichlet)
x = L   (skin surface)  −k ∂T/∂x = h (T_s − T_∞) + ε σ ( T_s⁴ − T_env⁴ )
```

**Exact solution.** In layer `i` with constant `k_i`, `ω_i`, `q_met,i`:

```
ω_i > 0 :   θ_i(x) = A_i cosh(κ_i x) + B_i sinh(κ_i x) + q_met,i /(ω_i ρ_b c_b)
ω_i = 0 :   θ_i(x) = A_i + B_i x − q_met,i x² /(2 k_i)
```

Interface conditions: continuity of `T` and of `k ∂T/∂x`. Together with the core
Dirichlet condition this reduces the whole stack to a **linear map from the surface
temperature `T_s` to the surface flux**. The radiative boundary condition then
closes it as a **single scalar nonlinear equation in `T_s`**, solved by Newton in the
reference implementation.

`【FACT】` The solution is exact in the sense that the only approximation is the
Newton tolerance on one scalar, which can be driven to machine precision.

**What it verifies.** Layered materials — absent from all three benchmarks of the
previous project. The `env_radiation` boundary condition, **which is implemented in
`yuchiri-axirad2D` but has never been compared with a reference solution.** The
`4εσT³` Jacobian term. The absence of spurious radial variation.

`【JUDGEMENT】` This is the only entry in which surface-to-surface radiation earns
its place in a biological problem. It should be said plainly: the Monte Carlo
enclosure machinery of the parent project has little use in tissue, because tissue
optics is participating-media transport, which is out of scope (§1.2).

---

## §8 Relationship to `yuchiri-axirad2D`

`【FACT】` The suite is **independent of any solver.** It is published so that other
codes can run it.

`【FACT】` The parent solver requires **one addition** to participate: the volumetric
perfusion term. Structurally it is the convection boundary condition integrated over
volume instead of over a surface: a residual contribution and a mass-like Jacobian
block.

`【DESIGN】` That addition belongs in `yuchiri-axirad2D` **v1.1**, together with the
three benchmarks as example cases, while this suite carries the problem definitions,
derivations, reference implementations and report schema.

`【JUDGEMENT】` Keeping them apart matters. If the benchmark lives inside the solver
that it grades, "the suite passes" means only "the code agrees with itself".

---

## §9 Open items — the author must decide

| # | Item | Note |
|---|---|---|
| **M-1** | **Name of the suite and of the repository** | Not decided |
| **M-2** | Width of the acceptance band on observed order (§4) | Risk of an unjustified constant; the alternative is to report `p` and fail only on `p < 1` |
| **M-3** | Norm used for the error — `L∞`, `L2`, or both | **Partly settled by §4**: whichever is used must be declared, because the expected order differs. DB-3 currently reports nodal `L∞` |
| **M-4** | Whether the suite **prescribes meshes** or only geometry | **Provisionally ③ (both)** — meshes shipped as the primary path, own-mesh runs accepted as an optional secondary report. Reason: DB-3 already ships three refinement levels, and the parent project's defect surfaced through meshing, so neither path should be discarded. **Awaiting the author's confirmation.** |
| **M-5** | Property values — physiological values, or dimensionless `κa` only | §6 argues the dimensionless grouping is sufficient and avoids arguing about tissue data |
| **M-6** | Transient benchmarks and thermal dose (CEM43, Arrhenius) | Deferred from v0.1. Clinically this is the meaningful output, so it will have to come |
| **M-7** | Licence for the suite | The parent project is MIT |
| **M-8** | Whether to seek alignment with ASME V&V 40 vocabulary explicitly | Would make the suite citable in a regulatory context; also invites scrutiny |

`【FACT】` M-4 is the one that changes the character of the suite most. It is asked
first in §10.

---

## §10 First question to the author

**Does the suite prescribe the meshes, or only the geometry?**

| Option | Gain | Cost |
|---|---|---|
| **Prescribed meshes shipped with the suite** | Two codes reporting different errors on the same mesh differ for a reason that is about the codes, not about meshing skill. Directly comparable | Requires a mesh format the suite owns, and excludes codes that cannot import it |
| **Geometry only; each code meshes it** | Tests the whole chain a real user goes through, meshing included — which is where the previous project's defect actually surfaced | Results are not strictly comparable between codes; a good result may come from a good mesh rather than a good solver |
| **Both: prescribed meshes as the primary path, own meshes as an optional secondary report** | Comparability and realism | Two paths to document and maintain |

`【FACT】` Nothing will be implemented until this is answered.

---
---

# 한국어

## §0 표기

| 표기 | 뜻 |
|---|---|
| `【사실】` | 물리 법칙, 수학적 정의, 또는 작성자가 이미 확정한 결정 |
| `【설계】` | 이 문서가 택한 것. 다른 선택도 가능했다 |
| `【해석】` | 판단·추정. 사실이 아니다 |
| `【미결】` | 확정되지 않았다. §9 에 모은다 |
| `【구현 재량】` | 이 문서가 의도적으로 정하지 않는다 |
| `**` | 근거가 불확실한 서술 |

## §1 목적과 비목적

### 1.1 이 모음이 무엇인가

`【사실】` 축대칭 생체열전달 솔버를 위한 **검증(verification)** 문제 모음이며,
참조값은 **이 문서에서 유도한 정확해**다. 수치표도 아니고 다른 코드의 출력도 아니다.

`【사실】` **코드에 독립적이다.** 명시된 형상·물성·경계조건을 부여할 수 있는 어떤
솔버도 수행할 수 있다.

### 1.2 이 모음이 무엇이 아닌가 — 먼저 읽을 것

`【사실】` **이것은 검증이지 확인(validation)이 아니다.** ASME V&V 40 의 용어로:

| | 답하는 질문 | 여기서 가능한가 |
|---|---|---|
| **검증** | 코드가 방정식을 맞게 푸는가 | **예** |
| **확인** | 그 방정식이 실제 조직을 기술하는가 | **아니오** |

`【사실】` **Pennes 방정식 자체가 법칙이 아니라 모델 가설이다.** 실측 조직 온도
분포가 등가전도도 모델과는 맞고 통상적 열싱크 관점과는 맞지 않는다는 보고가 있다.
이 모음의 모든 벤치마크를 통과해도, Pennes 식이 당신의 조직을 기술하는지에 대해서는
아무것도 말해 주지 않는다.

`【해석】` 이 한계는 모음의 약점이 아니라 **존재 이유**다. 확인이 어려운 분야 —
살아 있는 계 내부의 장은 측정할 수 없다 — 에서 검증은 **빈틈없이 만들 수 있는
유일한 부분**이며, 그렇게 만들어야 한다.

`【사실】` 범위 밖: 참여 매질 복사(조직 광학), 이방성 전도도, 대혈관 역류 모델,
상변화(극저온 소작), 전자기(SAR 은 **주어진 열원**으로 취급하며 풀지 않는다).

## §2 지배방정식

`【사실】` 정상 상태 Pennes 생체열방정식, 축대칭:

```
∇·( k(T) ∇T )  +  ω_b ρ_b c_b ( T_a − T )  +  q_met  +  q_ext  =  0
dV = 2π r dr dz
```

| 기호 | 뜻 | 단위 |
|---|---|---|
| `k` | 조직 열전도도 | W/(m·K) |
| `ω_b` | 혈액 관류율 | 1/s |
| `ρ_b c_b` | 혈액 체적 열용량 | J/(m³·K) |
| `T_a` | 동맥혈 온도 | K |
| `q_met` | 대사 발열 | W/m³ |
| `q_ext` | 외부 열원 (SAR·RF·레이저·자성) | W/m³ |

`【설계】` `θ = T − T_a` 와 **관류 길이척도**를 정의한다.

```
κ = √( ω_b ρ_b c_b / k )        [1/m]        L_p = 1/κ
```

`【사실】` 물성이 일정하면 동차 방정식이 `∇²θ = κ²θ` 가 된다.
**이 모음의 모든 정확해가 이 한 줄에서 나온다.**

`【설계】` v0.1 에 과도 문제는 **포함하지 않는다.** §9 M-6 참조.

## §3 벤치마크 항목의 필수 구성

`【설계】` 각 항목은 다섯 가지를 갖춘다. 하나라도 없으면 모음에 넣지 않는다.

| # | 항목 | 이유 |
|---|---|---|
| 1 | **문제 정의** — 형상·물성·경계조건. SI 단위, 자유 파라미터 없음 | 두 사람이 같은 문제를 만들도록 |
| 2 | **정확해의 유도** — 인용이 아니라 서술 | 독자가 도서관 없이 검산할 수 있도록 |
| 3 | **참조 구현** — 정확해를 계산하는 짧은 스크립트 | 수치가 옮겨 적힌 것이 아니라 재현되도록 |
| 4 | **합격 기준** — §4 | "통과"가 취향의 문제가 되지 않도록 |
| 5 | **보고 형식** — §5 | 서로 다른 코드의 결과를 비교할 수 있도록 |

`【사실】` **이 모음 어디에도 문헌의 수치표를 복제하지 않는다.** 모든 참조값은
항목 2의 식으로부터 항목 3이 계산한다.

## §4 합격 기준 — 허용오차가 아니라 수렴 차수

`【설계】` **벤치마크의 합격은 고정 오차 임계값이 아니라, 격자 세분에 따른 기대
수렴 차수의 실증으로 판정한다.**

`【해석】` 이유는 작성자가 일관되게 적용해 온 것이다 — **고정 허용오차는 근거 없는
상수**다. 격자·요소 차수·문제 규모에 의존하는데 그중 어느 것도 모음이 통제하지
않는다. 관측된 수렴 차수는 그렇지 않다.

`【설계】` 벤치마크마다 요구되는 보고:

```
최소 세 단계의 세분 h, h/2, h/4 에 대해
    e(h) = || T_계산 − T_정확 ||          (사용한 노름을 명시)
    관측 차수  p = log2( e(h) / e(h/2) )
```

**기대 차수는 무엇을 재느냐에 달려 있다.** 초안에서 이를 느슨하게 적었으므로
여기서 정정한다.

| 재는 대상 | 1차 요소 | 2차 요소 |
|---|---|---|
| **절점값의 L∞** | 2 | **4** — 1차원 절점 초수렴 |
| 장 전체의 L2 | 2 | 3 |
| 기울기 / 유속 | 1 | 2 |

`【사실】` **정정 기록.** v0.1 초안은 노름을 밝히지 않은 채 "2차 요소 → 3" 이라고
적었다. DB-3 에서 실측한 **절점 L∞ 오차의 관측 차수**는 **3.81 → 3.90**(공칭 관류),
**3.95 → 3.97**(약한 관류), **3.67 → 3.83**(강한 관류) 이었다. 이는 3 이 아니라
4 와 부합한다. 1차원에서 유한요소해의 절점값은 절점 사이의 장보다 빠르게 수렴하며,
차수 `p` 요소에서 `O(h^{2p})` 다. 위 표가 이제 그것을 말한다.

`【해석】` 이 정정은 합격 여부를 바꾸지 않는다. 강제 실패 조건이 `p < 1` 이기
때문이다. 그러나 **기대값을 틀리게 적은 벤치마크는 사용자에게 틀린 것을 받아들이도록
가르친다.**

`【미결】` M-2 — "명시된 대역"의 폭. 이것을 정하는 일이 바로 이 프로젝트가 피해 온
근거 없는 상수다. 후보 — **`p` 를 보고하고 판단은 독자에게 맡기되, `p < 1`(즉 아예
수렴하지 않음)일 때만 강제 실패**로 한다. `yuchiri-axirad2D` 의 야코비안 결함을
잡은 것이 정확히 그 조건이었다.

`【설계】` **추가로** 모든 항목이 임계값 없는 두 값을 보고한다.

* **전역 에너지 수지 잔차** — 발열 + 유입 = 유출, 반올림 수준까지
* **극한 검사** — `κ → 0` 에서 같은 형상의 순수 전도해로 환원되어야 한다.
  그 전도해는 별도로 알려져 있다

## §5 보고 형식

`【설계】` (코드, 벤치마크, 격자) 조합마다 JSON 파일 하나.

```
{ "suite_version", "benchmark_id", "code_name", "code_version",
  "element_type", "n_nodes", "n_elements", "characteristic_h",
  "error_Linf", "error_L2", "observed_order",
  "energy_residual_relative",
  "kappa_a",                      // 유일한 무차원 수. §6
  "notes" }
```

`【구현 재량】` 파일 배치, 도구, 실행기의 언어.

## §6 무차원화

`【사실】` 물성이 일정하면 형상 + 관류 문제는 **길이척도마다 무차원 수 하나**에만
의존한다.

```
DB-1, DB-2 :  κa        (관류 길이 대 적용기 반경)
              b/a       (외경 대 적용기 반경)
DB-3       :  층마다 κ_i L_i
```

`【설계】` 각 벤치마크는 **영역을 가로지르는 세 개의 `κa` 값**에서 수행한다.

| 영역 | `κa` | 물리적 의미 |
|---|---|---|
| 전도 지배 | 0.1 | 관류가 거의 무의미. 순수 전도해에 접근해야 한다 |
| 균형 | 1 | 흥미로운 경우 |
| 관류 지배 | 10 | 열원 근처에 얇은 열경계층 |

`【해석】` `κa = 10` 이 까다로운 경우다. 얇은 층이 생겨 성긴 격자가 뭉갠다.
**`κa = 0.1` 에서만 통과한 코드는 시험된 것이 아니다.**

---

## §7 세 벤치마크

### DB-1 — 관류 조직 내 구면 표면열원

**물리적 설정.** 자기유체 온열치료 — 구형 종양 표면의 자성 나노입자 박막층이
총 전력 `P` 를 낸다.

**형상.** 구각 `a ≤ r ≤ b`, 축대칭(구는 회전체다). 내면 `r = a` 에 총 `P` 의
유입 유속, 외면 `r = b` 는 `T_a` Dirichlet.

`【설계】` `r < a_0 < a` 는 격자로 만들지 않는다. 중심에서 요소가 퇴화하는 것을
피하기 위함이며, `yuchiri-axirad2D` BM-5 에서 쓴 것과 같은 방식이다.

**정확해.** `θ = T − T_a` 로 두면

```
(1/r²)(r² θ′)′ = κ² θ        ⇒    θ(r) = A e^(−κr)/r  +  B e^(+κr)/r
```

`θ(b) = 0` 과 `P = 4πa²·(−k θ′(a))` 로부터 `A, B` 가 닫힌 형태로 나온다.

무한 매질 극한 `b → ∞` (`B = 0`):

```
θ(r) = P · e^(−κ(r−a)) / [ 4π k r (1 + κa) ]
θ(a) = P / [ 4π k a (1 + κa) ]
```

`【사실】` 정합 극한 — `κ → 0` 이면 `θ(r) → P/(4πkr)`, 고전적 점열원 전도해다.
§4 의 `κ → 0` 극한 검사가 이것이다.

**검증되는 것.** 관류 항 자체, 구 사상, 표면 유속 경계조건, `κ → 0` 환원.

**재사용.** `【해석】` BM-5 의 극좌표 격자 생성기, 축 스냅 처리, 검증 스크립트가
거의 그대로 옮겨 간다. **셋 중 가장 값싸며 첫 번째로 해야 한다.**

---

### DB-2 — 관류 조직 내 원통형 적용기

**물리적 설정.** 조직에 삽입된 반경 `a` 의 RF·마이크로파·레이저 소작 프로브.

**형상.** 환형 `a ≤ r ≤ b`, 축 길이 `L`, **양단 단열**이므로 해가 `r` 만의 함수다.
`r = a` 에 단위 길이당 `P′` 의 유입 유속, `r = b` 에 `T_a` Dirichlet.

**정확해.**

```
(1/r)(r θ′)′ = κ² θ        ⇒    θ(r) = A K₀(κr) + B I₀(κr)
θ′(r) = κ [ −A K₁(κr) + B I₁(κr) ]
```

`θ(b) = 0` 과 `P′ = 2πa·(−k θ′(a))` 로 `A, B` 결정. `K₀, K₁, I₀, I₁` 은 변형 Bessel
함수이며 참조 구현이 계산한다.

`【사실】` 정합 극한 — `κ → 0` 이면 `θ(r) → (P′/2πk)·ln(b/r)`, 고전적 원통 전도해다.
`yuchiri-axirad2D` 에서 이미 검증 사례로 쓴 `ln r` 분포와 같다.

**검증되는 것.** `【해석】` **비자명한 특수함수 참조값.** 이전 프로젝트에서 닫힌
형태 형상계수가 BM-2 에 대해 했던 역할을 여기서 한다 — 정확해가 0 도 1 도 지수함수도
아닌 첫 벤치마크다. 또한 축대칭 `2πr` 가중치와 관류 항의 상호작용을 시험한다.
**둘 다 맞아야만 답이 나온다.**

**피해야 할 함정.** `【해석】` 양단 단열 이상화는 **실제로 단열일 때만** 정확하다.
코드가 거기에 다른 것을 조용히 적용하면 그 오차가 이산화 오차처럼 보인다.
**보고서는 축 방향 경계조건을 명시해야 한다.**

---

### DB-3 — 관류가 있는 다층 피부와 복사 표면 손실

**물리적 설정.** 실내에 노출된 피부 — 표피·진피·피하지방 3층, 전도도와 관류율이
서로 다르며, 표면에서 **대류와 복사**로 열을 잃는다.

**형상.** 반경 `R`, 두께 `L` 의 원통, **측면 단열**이므로 정확해가 축좌표만의
함수다. `【해석】` 여기에는 두 번째 목적이 있다 — 올바른 축대칭 코드는 **r 의존성이
전혀 없는** 장을 내놓아야 한다. **반경 방향 변화가 나타나면 그것이 결함 신호다.**

**경계조건.**

```
x = 0   (심부)      T = T_core                     (Dirichlet)
x = L   (피부 표면)  −k ∂T/∂x = h (T_s − T_∞) + ε σ ( T_s⁴ − T_env⁴ )
```

**정확해.** `k_i`, `ω_i`, `q_met,i` 가 일정한 층 `i` 에서

```
ω_i > 0 :   θ_i(x) = A_i cosh(κ_i x) + B_i sinh(κ_i x) + q_met,i /(ω_i ρ_b c_b)
ω_i = 0 :   θ_i(x) = A_i + B_i x − q_met,i x² /(2 k_i)
```

계면 조건은 `T` 와 `k ∂T/∂x` 의 연속. 심부 Dirichlet 과 함께 놓으면 전체 적층이
**표면 온도 `T_s` 에서 표면 유속으로 가는 선형 사상**으로 축약된다. 복사 경계조건이
이를 **`T_s` 에 대한 스칼라 비선형 방정식 하나**로 닫으며, 참조 구현이 Newton 으로
푼다.

`【사실】` 유일한 근사가 **스칼라 하나에 대한 Newton 허용오차**이고 이를 기계
정밀도까지 낮출 수 있으므로, 이 해는 정확하다.

**검증되는 것.** 다층 재료 — 이전 프로젝트의 벤치마크 3종에 없던 것.
`env_radiation` 경계조건 — **`yuchiri-axirad2D` 에 구현되어 있으나 참조해와 대조된
적이 한 번도 없다.** `4εσT³` 야코비안 항. 그리고 허위 반경 변화의 부재.

`【해석】` 표면 대 표면 복사가 생물학 문제에서 제 몫을 하는 **유일한 항목**이다.
분명히 적어 둔다 — 모(母) 프로젝트의 몬테카를로 enclosure 기계는 조직에서 쓸 데가
거의 없다. 조직 광학은 참여 매질 수송이고 그것은 범위 밖이다(§1.2).

---

## §8 `yuchiri-axirad2D` 와의 관계

`【사실】` 이 모음은 **어떤 솔버에도 독립적이다.** 다른 코드가 수행할 수 있도록
공개한다.

`【사실】` 모 솔버가 참여하려면 **한 가지 추가**가 필요하다 — 체적 관류 항.
구조적으로는 **대류 경계조건을 면이 아니라 체적에 대해 적분한 것**이며, 잔차 기여
한 블록과 질량행렬형 야코비안 블록이다.

`【설계】` 그 추가는 `yuchiri-axirad2D` **v1.1** 에 속하고, 세 벤치마크는 그
저장소에 예제로 들어간다. 이 모음은 문제 정의·유도·참조 구현·보고 형식을 담는다.

`【해석】` **둘을 분리하는 것이 중요하다.** 채점하는 벤치마크가 채점받는 솔버 안에
있으면, "모음을 통과했다"는 말은 "코드가 자기 자신과 일치한다"는 뜻밖에 되지 않는다.

---

## §9 미결 — 작성자가 결정해야 한다

| # | 항목 | 비고 |
|---|---|---|
| **M-1** | **모음과 저장소의 이름** | 미정 |
| **M-2** | 관측 차수 합격 대역의 폭 (§4) | 근거 없는 상수의 위험. 대안은 `p` 를 보고하고 `p < 1` 에서만 실패 |
| **M-3** | 오차 노름 — `L∞`, `L2`, 또는 둘 다 | **§4 에서 일부 확정**: 기대 차수가 달라지므로 무엇을 썼는지 반드시 밝혀야 한다. DB-3 는 현재 절점 `L∞` 를 보고한다 |
| **M-4** | 모음이 **격자를 지정**하는가, 형상만 주는가 | **잠정 ③ (둘 다)** — 격자를 주경로로 배포하고, 자체 격자 결과를 선택적 부가 보고로 받는다. 근거: DB-3 격자가 이미 3단계로 만들어져 있고, 모 프로젝트의 결함이 격자 쪽에서 드러났으므로 어느 경로도 버릴 수 없다. **작성자 확인 대기.** |
| **M-5** | 물성값 — 생리학적 값인가, 무차원 `κa` 만인가 | §6 은 무차원 수로 충분하며 조직 데이터 논쟁을 피할 수 있다고 본다 |
| **M-6** | 과도 벤치마크와 열용량(CEM43, Arrhenius) | v0.1 에서 보류. 임상적으로 의미 있는 산출이므로 결국 필요해진다 |
| **M-7** | 모음의 라이선스 | 모 프로젝트는 MIT |
| **M-8** | ASME V&V 40 용어와의 명시적 정합을 추구할 것인가 | 규제 맥락에서 인용 가능해진다. 동시에 검증의 표적이 된다 |

`【사실】` **M-4 가 모음의 성격을 가장 크게 바꾼다.** §10 에서 먼저 묻는다.

---

## §10 작성자에게 드리는 첫 질문

**모음이 격자를 지정합니까, 형상만 줍니까?**

| 선택지 | 얻는 것 | 잃는 것 |
|---|---|---|
| **격자를 모음이 배포** | 같은 격자에서 두 코드의 오차가 다르면, 그 차이는 격자 실력이 아니라 코드에 관한 것이다. 직접 비교 가능 | 모음이 소유하는 격자 형식이 필요하고, 그것을 읽지 못하는 코드는 배제된다 |
| **형상만 주고 각자 격자 생성** | 실제 사용자가 거치는 전 과정을 시험한다. **이전 프로젝트의 결함도 격자 쪽에서 드러났다** | 코드 간 비교가 엄밀하지 않다. 좋은 결과가 좋은 솔버가 아니라 좋은 격자에서 왔을 수 있다 |
| **둘 다 — 지정 격자를 주경로로, 자체 격자를 선택적 부가 보고로** | 비교 가능성과 현실성을 함께 | 유지할 경로가 둘 |

`【사실】` 이 답을 받기 전에는 **아무것도 구현하지 않는다.**
