# yuchiri-axibio-bench

**Verification benchmarks for axisymmetric bioheat solvers**
**축대칭 생체열전달 솔버를 위한 검증 벤치마크**

Suite version 0.2.0 · MIT · free, no strings

---

# English

## What this is

A set of **verification** problems for solvers of the steady Pennes bioheat
equation in axisymmetric geometry. For each problem the reference is an **exact
solution derived in this repository** — not a table copied from a publication,
and not the output of another code.

It is **code-independent**. Any solver that can impose the stated geometry,
properties and boundary conditions can run it and report in the schema.

> **Before using anything here, read [`DISCLAIMER.md`](DISCLAIMER.md).** It states
> that this software has **no intended medical purpose**, that it is verification
> and not validation, and that the numbers here are not measurements of a person.
> **사용 전 [`DISCLAIMER.md`](DISCLAIMER.md) 를 읽을 것.** 의도된 의료 목적이 없고,
> 검증이지 확인이 아니며, 여기의 숫자가 사람을 측정한 값이 아님을 밝힌다.

## What this is not — read before using

**Verification, not validation.**

| | Question | Answered here |
|---|---|---|
| Verification | Does the code solve the equations correctly? | **Yes** |
| Validation | Do those equations describe real tissue? | **No** |

**The Pennes equation is a modelling hypothesis, not a law.** Passing every
benchmark here says nothing about whether it describes your tissue. This limit is
not a weakness; it is the reason the suite is worth having. Where validation is
hard — you cannot measure the field inside a living system — verification is the
part that can be made airtight, and it should be.

## Run it on a fresh machine / 새 컴퓨터에서 실행

Nothing needs to be compiled and no solver is required. Python 3.9 or newer and
NumPy are enough. Tested on Linux and written to run unchanged on macOS
(including Apple Silicon) and Windows.

컴파일할 것이 없고 솔버도 필요 없다. Python 3.9 이상과 NumPy 면 된다.

```bash
python3 -m pip install numpy

cd benchmarks/db3_layered_skin/exact

# 1. the problem, in numbers
python3 db3_properties.py

# 2. regenerate the reference values and check them against four
#    independently known limits
python3 run_reference.py

# 3. check a submitted report against the acceptance criterion
python3 check_report.py ../results/yuchiri-axirad2D_v2.0.json
```

Step 2 rewrites `reference_values.json`; add `--check-only` to print without
writing. If your numbers differ from the ones committed here, something in your
environment differs — that is worth knowing before you trust any solver against
this benchmark.

2단계는 `reference_values.json` 을 다시 쓴다. 쓰지 않으려면 `--check-only`.
여기 커밋된 값과 다르게 나온다면 환경이 다른 것이며, 이 벤치마크로 어떤 솔버를
판정하기 전에 알아 두어야 할 사실이다.

### Running your own code against it / 자기 코드로 돌려 보기

The meshes are shipped **twice**: `db3_rN.mesh.npz` for `yuchiri-axirad2D`, and
`db3_rN.mesh.txt` in a plain text format any code can read. See
`benchmarks/db3_layered_skin/meshes/MESH_FORMAT.md`, which includes a reader in
about fifteen lines of Python.

격자는 **두 벌**로 배포한다. `.npz` 는 특정 솔버용, `.txt` 는 **어떤 코드도 읽을 수
있는 평문**이다. 형식과 15줄짜리 읽기 예가 `MESH_FORMAT.md` 에 있다.

Write your result as a JSON report in the schema of `SPEC.md` section 5 and run
`check_report.py` on it.

## Benchmarks

| ID | Problem | Verifies |
|---|---|---|
| **DB-3** | Layered skin, perfusion, convective + radiative surface loss | perfusion sink incl. an avascular layer; layered materials; nonlinear radiative BC and its `4εσT³` Jacobian; absence of spurious radial variation |
| DB-1 | *(planned)* Spherical surface source in perfused tissue | perfusion term, spherical mapping, `κ → 0` reduction |
| DB-2 | *(planned)* Cylindrical applicator | non-trivial special-function reference (modified Bessel) |

## Acceptance — order, not tolerance

A benchmark is passed by demonstrating the **expected order of convergence** on
the shipped `h`, `h/2`, `h/4` meshes, **not** by meeting a fixed error threshold.
A fixed tolerance would be an unjustified constant: it depends on the mesh, the
element order and the problem scale, none of which the suite controls.

**The expected order depends on the norm.** For quadratic elements the nodal
`L∞` error converges at order **4** in one dimension, not 3 — nodal
superconvergence. Report which norm you used. See `SPEC.md` §4.

Every entry also reports two threshold-free quantities: the **energy balance
residual** and, where the exact solution is one-dimensional, the **radial
variation**, which must be zero.

## Reported results

| Code | Version | DB-3 nodal L∞, finest mesh | Observed order | Report |
|---|---|---|---|---|
| yuchiri-axirad2D | 2.0.0 | 7.42e-09 K (nominal), 5.15e-10 K (weak), 1.10e-07 K (strong) | 3.90 / 3.97 / 3.83 | `benchmarks/db3_layered_skin/results/` |

## Figures

| Figure | Shows |
|---|---|
| `benchmarks/db3_layered_skin/figures/db3_numerical_results.png` | Seven panels: profile vs exact, mesh convergence with the observed order, where the error lives, Newton convergence, the 2D field, spurious radial variation, and a summary table |
| `benchmarks/db3_layered_skin/figures/db3_biological_meaning.png` | Two panels: how blood flow sets the surface temperature, and the heat budget of the skin |

| `benchmarks/db3_layered_skin/figures/db3_claims_and_coefficients.png` | Three panels showing **which physical claims the coefficients actually support** — the radiation-to-convection ratio across the whole reported range of `h`, the two non-overlapping coefficient intervals, and where the claim stops when air moves |

Guides to the figures are in `benchmarks/db3_layered_skin/docs/`, including
**`claims_and_coefficients.md`**, a short report separating the claim the
coefficients do support from the one they do not.

## Layout

```
SPEC.md                                    the specification
benchmarks/db3_layered_skin/
  problem.md              definition, property provenance, derivation, limits
  exact/db3_properties.py geometry and properties       (standalone, numpy only)
  exact/db3_exact.py      the exact solution            (standalone, numpy only)
  exact/run_reference.py  regenerate and self-check     (standalone, numpy only)
  exact/check_report.py   grade a submitted report      (standalone, numpy only)
  reference_values.json   generated reference numbers
  meshes/                 h, h/2, h/4 as .npz and as plain text, plus MESH_FORMAT.md
  results/                one JSON per code that has run it
  figures/                result figures and the script that regenerates them
  docs/                   how to read each figure (bilingual)
FILE_GUIDE.md                                every file, one line each (bilingual)
requirements.txt                             numpy; matplotlib only for figures
```

**Everything under `exact/` runs without a solver.** That is not a convenience,
it is the point: a reference that comes from the thing it is grading is not a
reference.
**`exact/` 아래는 전부 솔버 없이 실행된다.** 편의가 아니라 요점이다. 채점 대상에서
나온 참조값은 참조값이 아니다.

## 도면 / Figures (한국어)

| 도면 | 내용 |
|---|---|
| `figures/db3_numerical_results.png` | 7패널 — 정확해 대조, 격자 수렴과 관측 차수, 오차의 분포, Newton 수렴, 2차원 온도장, 허위 반경 변화, 종합표 |
| `figures/db3_biological_meaning.png` | 2패널 — 혈류가 표면 온도를 정하는 방식, 피부의 열수지 |

| `figures/db3_claims_and_coefficients.png` | 3패널 — **계수가 실제로 뒷받침하는 주장이 무엇인가.** `h` 의 보고 범위 전체에서의 복사/대류 비, 겹치지 않는 두 계수 구간, 바람이 불면 주장이 멈추는 지점 |

도면을 읽는 법은 `benchmarks/db3_layered_skin/docs/` 에 있으며, 계수가 뒷받침하는
주장과 그렇지 않은 주장을 갈라 놓은 짧은 보고서 **`claims_and_coefficients.md`**
도 거기에 있다.

## Licence and provenance

MIT. Copyright (c) 2026 Yoo Cheol WON. Free of charge, no consideration of any
kind. `COPYRIGHT.md`.

**"MIT License" is the historical name of a standard permissive licence form. It
implies no connection with the Massachusetts Institute of Technology.**

Written with Anthropic's Claude as a tool; the design decisions are the author's.

---

# 한국어

## 이것이 무엇인가

축대칭 정상 Pennes 생체열방정식 솔버를 위한 **검증** 문제 모음이다. 각 문제의
참조값은 **이 저장소에서 유도한 정확해**이며, 문헌에서 복제한 표도 아니고 다른
코드의 출력도 아니다.

**코드에 독립적이다.** 명시된 형상·물성·경계조건을 부여할 수 있는 어떤 솔버도
수행하고 정해진 형식으로 보고할 수 있다.

## 이것이 아닌 것 — 쓰기 전에 읽을 것

**검증이지 확인이 아니다.**

| | 질문 | 여기서 답하는가 |
|---|---|---|
| 검증 | 코드가 방정식을 맞게 푸는가 | **예** |
| 확인 | 그 방정식이 실제 조직을 기술하는가 | **아니오** |

**Pennes 식은 법칙이 아니라 모델 가설이다.** 여기의 모든 벤치마크를 통과해도, 그
식이 당신의 조직을 기술하는지에 대해서는 아무것도 말해 주지 않는다. 이 한계는
약점이 아니라 이 모음의 존재 이유다. 확인이 어려운 곳 — 살아 있는 계 내부의 장은
측정할 수 없다 — 에서 검증은 빈틈없이 만들 수 있는 유일한 부분이며, 그렇게 만들어야
한다.

## 벤치마크

| ID | 문제 | 검증하는 것 |
|---|---|---|
| **DB-3** | 다층 피부, 관류, 대류 + 복사 표면 손실 | 무혈관 층을 포함한 관류 열싱크, 다층 재료, 비선형 복사 BC 와 `4εσT³` 야코비안, 허위 반경 변화의 부재 |
| DB-1 | *(예정)* 관류 조직 내 구면 표면열원 | 관류 항, 구 사상, `κ → 0` 환원 |
| DB-2 | *(예정)* 원통형 적용기 | 비자명한 특수함수 참조값 (변형 Bessel) |

## 합격 판정 — 허용오차가 아니라 차수

배포된 `h`, `h/2`, `h/4` 격자에서 **기대 수렴 차수를 실증**해 합격한다. 고정 오차
임계값으로 판정하지 **않는다.** 고정 허용오차는 근거 없는 상수다 — 격자, 요소 차수,
문제 규모에 의존하는데 모음이 그중 아무것도 통제하지 않는다.

**기대 차수는 노름에 따라 다르다.** 2차 요소에서 절점 `L∞` 오차는 1차원에서 3 이
아니라 **4** 차로 수렴한다(절점 초수렴). 어떤 노름을 썼는지 밝혀야 한다.
`SPEC.md` §4 참조.

모든 항목은 임계값 없는 두 값도 보고한다 — **에너지 수지 잔차**, 그리고 정확해가
1차원인 경우 0 이어야 하는 **반경 변화**.

## 보고된 결과

| 코드 | 버전 | DB-3 최밀 격자 절점 L∞ | 관측 차수 | 보고서 |
|---|---|---|---|---|
| yuchiri-axirad2D | 2.0.0 | 7.42e-09 K (공칭), 5.15e-10 K (약함), 1.10e-07 K (강함) | 3.90 / 3.97 / 3.83 | `benchmarks/db3_layered_skin/results/` |

## 라이선스와 계보

MIT. Copyright (c) 2026 원유철. 어떠한 대가도 없이 무상 공개.

**"MIT 라이선스" 는 표준 허가형 라이선스 양식의 관용적 명칭이며 매사추세츠
공과대학교와 관련이 없다.**

Anthropic 의 Claude 를 도구로 사용해 작성했으며, 설계 결정은 저작자의 것이다.
