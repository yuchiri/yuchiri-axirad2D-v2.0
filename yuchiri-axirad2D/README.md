# yuchiri-axirad2D

**A general-purpose 2D axisymmetric conduction–radiation finite element solver**
**범용 2차원 축대칭 전도–복사 유한요소 해석기**

*English first · 한국어는 아래에 이어집니다*

---
---

# English

Takes geometry, mesh and material properties as **input** and computes the
temperature field. Surface radiation is solved by Monte Carlo ray tracing for
Gebhart absorption factors, **fully coupled** to conduction through a Newton solver.

## What it does

```
∇·( k(T) ∇T ) + q_vol = 0            axisymmetric,  dV = 2πr dr dz
```

coupled with surface-to-surface radiation.

* **Five element types** — 3/6-node triangles, 4/8/9-node quadrilaterals,
  **mixable within a single mesh**. Triangles and mixed meshes are validated by a
  mesh-convergence study against the `ln r` analytic solution and by a patch test
* **Automatic radiating-surface extraction** — tag materials transparent or
  opaque; the code finds the surfaces and the enclosures
* **Enclosure count is never hard-coded** — as many as the mesh yields
* **Five boundary condition types** — Dirichlet, heat flux, adiabatic/symmetry,
  convection, environment radiation
* **Parallel** — serial or MPI. **Results are bit-for-bit identical** (measured)

## What it does not do

* Does not generate meshes (mesh is entirely external input)
* Contains no geometry coordinates of any device
* No participating-media radiation (absorption / scattering)
* No anisotropic properties

## Design principles — fail loudly, never silently

This code **never auto-corrects**. All of the following are deliberate.

| Principle | Meaning |
|---|---|
| **Closure is not renormalised** | If `Σ_b B_ab < 1` it is not padded to 1. Leakage is counted by cause and **aborts** above a threshold |
| **Reciprocity is not symmetrised** | The discrepancy tells you the size of the statistical error. Forcing it destroys that information |
| **Normals are not inherited from endpoint order** | Determined topologically, cross-checked geometrically. **Mismatch aborts** |
| **No pre-selection of blocking candidates** | Every ray is tested against **all** surfaces for the nearest intersection |
| **Convergence is an AND condition** | Both the temperature increment **and** the energy imbalance must be satisfied |
| **No switch disables a check** | Aborts, but always writes the diagnostics file first |
| **No unjustified constants** | e.g. the G4 tolerance is not a fixed number but `64·n_elem·ε_machine`, **derived from the number of terms** |

## Reproducibility — measured

Nodal temperature fields from `serial`, `mpi(1)`, `mpi(2)` and `mpi(4)` are
**bit-for-bit identical**.

```
reference: serial   435 nodes
  mpi n=1 : bitwise equal = True   max diff 0.000e+00
  mpi n=2 : bitwise equal = True   max diff 0.000e+00
  mpi n=4 : bitwise equal = True   max diff 0.000e+00
```

**Why this works** — random numbers are determined by (segment, bounce) and
indexed by ray id, making the result batch-invariant; partial results are
**placed** in rank order rather than summed, so floating-point addition order
never enters.

**The cost** — every process holds a full-size coefficient matrix, so memory
grows with process count, and communication is not optimised. That is the price
of reproducibility.

## Install and run on a fresh machine

Pure Python; nothing is compiled.

* **Python 3.11 or newer** — NumPy and SciPy are all that is needed.
* **Python 3.9 or 3.10** — also works, but add `pip install tomli`. The problem
  file is TOML, and a TOML reader only entered the standard library in 3.11.
  macOS ships 3.9 with the Xcode command line tools, so this is the common case
  on a Mac unless you install a newer Python.

Written to run unchanged on Linux, macOS (including Apple Silicon) and Windows;
the figure scripts pick a Korean-capable font automatically and fall back
silently if none is present.

```bash
pip install numpy scipy
pip install pytest     # to run the tests
pip install mpi4py     # only if you use MPI
export PYTHONPATH=src
```

## Run

```bash
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
mpirun -n 4 python -m axirad2d.cli examples/bm2_bm5/case_bm2.toml   # parallel = "mpi"
bash run_all.sh        # meshes → 63 tests → benchmarks → analytic comparison
```

## Reproducibility of the shipped outputs

The example outputs committed here are not decoration: they regenerate **byte for
byte** on a fresh machine. Verified by extracting the release archive twice into
clean directories and recomputing everything.

| Regenerates identically | Does not |
|---|---|
| every mesh `.npz`, `results.npz`, `temperature.csv`, the reference values, and **the figure PNGs** | `time_radiation_s` and `time_total_s` in `diagnostics.json` — wall clock, so they cannot |

Check it yourself:

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5:examples/db3
python3 tools/check_reproducibility.py      # ends with REPRODUCIBLE
```

It copies the committed outputs aside, recomputes them, compares bit for bit, and
names the two timing fields it ignores rather than hiding them.

## Benchmarks

Three benchmarks. **Every reference value is computed directly from a published
closed-form expression.** No numerical table from any publication is reproduced.

| | BM-1 coaxial cavity | BM-2 finite cylinder cavity | BM-5 concentric spheres |
|---|---|---|---|
| Surfaces | planar / straight | planar / straight | **curved (frustum approx.)** |
| View factors | trivial (0, 1) | **non-trivial (0.1716)** | trivial (0, 1) |
| Emissivity | exact for black wall | all black | **gray (exact)** |
| Basis of exact solution | convex body fully enclosed | closed-form view factor | uniform irradiation by symmetry |
| Error vs exact | +0.0019 % / +0.0081 % | −0.041 % / +0.029 % | −0.035 % / +0.0320 % |
| Newton iterations | 6 | 4 | 9 |
| Energy residual | 1.1e-12 | 5.3e-15 | 5.7e-14 |

**All 15 compared quantities lie within 0.06 % of exact; 8 of them match exactly.**

Definitions and drawings — `docs/BENCHMARK_PROBLEMS.md`,
`figures/benchmark_definitions.png`.
Figures — `figures/results_temperature_fields.png`, `figures/results_verification_summary.png`.
Full tables — `docs/BENCHMARK_RESULTS.md`.

**Bioheat (v2.0).** The Pennes perfusion term is a **volumetric source, not
convection**: there is no velocity field and no advection term anywhere in this
code, so within the tissue conduction remains the only transport mechanism.
See `docs/USER_GUIDE.md` section 5a. It is verified against benchmark
**DB-3** of the separate suite `yuchiri-axibio-bench`: nodal L∞ error 7.4e-09 K on
the finest mesh, observed order 3.90, spurious radial variation 2.8e-13 K.
See `examples/db3/`.

### ⚠ Do not use the lumped two-surface gray formula as a verification target

```
Q = σ(T₁⁴−T₂⁴) / [ (1−ε₁)/(ε₁A₁) + 1/(A₁F₁₂) + (1−ε₂)/(ε₂A₂) ]
```

This expression **additionally assumes uniform radiosity on each surface.**
A cylindrical cavity wall is irradiated non-uniformly, so the assumption fails.

Measured: with ε₂ = 0.6 the difference from this code was **≈ 1.6 %**, and it
**did not shrink** when rays were increased from 10,000 to 80,000 — a systematic
bias, not noise. With ε₂ = 1.0 (assumption not needed) the difference fell to
**0.005 %**. In concentric spheres, where symmetry makes irradiation uniform,
it is **0.035 %**.

**The deviation comes from the formula's own assumption, not from the code.**
Without knowing this, a correct code can be misjudged as 1.6 % wrong.

## Known limitations — read before trusting results

1. **Cyclic node rotation, misplaced mid-side nodes and wrong node counts may go
   undetected.** This is the price of introducing no unjustified thresholds.
2. **Mid-side nodes of quadratic elements receive no radiative flux.** Radiating
   segments are straight frusta defined by two corner nodes.
3. **Conduction and radiation see different geometry** — curved edges vs straight
   approximation.
4. **Monte Carlo statistical error propagates into the solution and does not
   shrink with iteration.** Gebhart factors are computed once per run; vary the
   ray count yourself to assess it.
5. **Tolerances tighter than the statistical noise always end in convergence
   failure.**
6. **MPI reproducibility costs memory proportional to process count.**
7. **Transparent materials need a small non-zero `k`.** With `k = 0` the equations
   for interior nodes of that region become singular. Temperatures plotted there
   have no physical meaning.

Full statement in `DISCLAIMER.md`.

## Documents

| Document | Contents |
|---|---|
| `COPYRIGHT.md` | **Copyright holder and free-release declaration** |
| `DISCLAIMER.md` | **No-warranty notice — read before use** |
| `docs/USER_GUIDE.md` | Install, input formats, running, diagnostics, abort messages |
| `docs/BENCHMARK_PROBLEMS.md` | **Benchmark problem definitions, drawings, exact answers, sources** |
| `docs/BENCHMARK_RESULTS.md` | All 15 exact comparisons, reproduction commands |
| `CONTRIBUTING.md` | The seven design principles that must not be broken |
| `CHANGELOG.md` | Release history |

All documents are bilingual (English / Korean).
**In-code comments and runtime messages are in Korean.** English glosses for
every abort message are in `docs/USER_GUIDE.md` §11.

## Implementation status

| Implemented | Not implemented |
|---|---|
| Five element types (incl. triangles and mixed meshes, convergence-verified) | Transient (backward Euler) |
| **Pennes perfusion and metabolic heat** (v2.0) | |
| Mesh checks G1/G2/G4, patch test, non-axis-aligned gradient test | |
| Automatic surface extraction, normal cross-check | Schur static condensation |
| Monte Carlo Gebhart, leakage abort | Some detailed outputs |
| Fully coupled Newton, AND convergence | |
| Five BC types, TOML I/O, standard diagnostics | |
| MPI parallel with bit-for-bit reproducibility | |

## Modules

```
src/axirad2d/
  elements.py    shape functions (5 types), quadrature
  mesh.py        mesh, topology, checks G1/G2/G4, fingerprint
  materials.py   temperature polynomials, analytic derivatives
  surfaces.py    radiating-surface extraction, enclosures, normal cross-check
  montecarlo.py  ray tracing, Gebhart factors, leakage & reciprocity diagnostics
  assemble.py    boundary conditions, global residual and Jacobian
  solve.py       Newton, driver, MPI coupling
  problemio.py   TOML input, results and diagnostics output
  cli.py         command line
```

## AI use disclosure

This software was written **using Anthropic's Claude as a tool.**

The design was decided by a human. Mesh input strategy, element types, radiating
surface extraction, normal determination and mismatch handling, boundary
condition types, heat source input, coupling scheme, convergence criterion,
parallel strategy and reproducibility policy, output level — **more than twenty
design decisions were chosen by a human from presented options, and those
decisions determine the structure of the code.** The choice of benchmark
geometries and their exact solutions, and the judgement that the lumped gray
formula is unfit as a verification target, are also the human author's.

Claude was used to turn those decisions into code and tests.

## Provenance

This code contains **no geometry coordinates of any device, no material
coefficients for any specific substance, and no boundary conditions of any
specific problem.** Geometry, mesh, materials, heat sources and boundary
conditions are all input.

The algorithms are all public knowledge — Galerkin FEM, isoparametric elements,
Gauss quadrature, Gebhart absorption factors, Monte Carlo ray tracing,
Newton–Raphson, backward Euler.

Benchmark reference values are **computed directly** from published expressions;
no numerical table is reproduced.

## License

MIT. See `LICENSE`. Copyright (c) 2026 **Yoo Cheol WON**.
Released free of charge with no consideration of any kind — see `COPYRIGHT.md`.

> **On the name.** "MIT License" is the historical name of a standard permissive
> licence form. It implies **no connection with, and no endorsement by, the
> Massachusetts Institute of Technology**. The copyright holder of this software
> is Yoo Cheol WON.

## Citation

See `CITATION.cff`.

---
---

# 한국어

형상·격자·물성을 **입력으로 받아** 온도 분포를 계산한다. 표면 복사는 몬테카를로
광선 추적으로 Gebhart 흡수계수를 구하고, 전도와 **완전 결합 Newton** 으로 푼다.

## 무엇을 하는가

```
∇·( k(T) ∇T ) + q_vol = 0            축대칭,  dV = 2πr dr dz
```

에 표면 대 표면 복사를 결합한다.

* **요소 5종** — 삼각형 3·6절점, 사각형 4·8·9절점. **한 격자에 혼합 가능**.
  삼각형과 혼합 격자는 `ln r` 해석해 대비 격자 수렴과 패치 시험으로 검증되었다
* **복사면 자동 추출** — 재료의 투명/불투명 표시만 주면 코드가 면과 enclosure 를 찾는다
* **enclosure 개수를 하드코딩하지 않는다** — 격자에서 나오는 대로 몇 개든
* **경계조건 5종** — Dirichlet, 열유속, 단열/대칭, 대류, 환경 복사
* **병렬** — 직렬 / MPI 선택. **결과는 비트 단위로 동일**하다 (실측 확인)

## 무엇을 하지 않는가

* 격자를 만들지 않는다 (전량 외부 입력)
* 어떤 장치의 형상 좌표도 내장하지 않는다
* 참여 매질 복사(흡수·산란)를 다루지 않는다
* 이방성 물성을 다루지 않는다
* **물질전달을 다루지 않으며, 따라서 증발 냉각이 없다.** 표면은 이웃으로의 전도,
  대류, 복사로만 열을 잃는다

## 설계 원칙 — 조용히 틀리느니 멈춘다

이 코드는 **자동 보정을 하지 않는다.** 아래는 전부 의도된 설계다.

| 원칙 | 내용 |
|---|---|
| **폐쇄성을 보정하지 않는다** | `Σ_b B_ab` 가 1 에 미달해도 1 로 채우지 않는다. 누출은 원인별로 계수하고 임계값을 넘으면 **중단**한다 |
| **상반성을 대칭화하지 않는다** | 어긋남은 통계 오차의 크기를 알려주는 정보다. 강제로 맞추면 그 정보가 사라진다 |
| **법선을 끝점 순서에서 상속받지 않는다** | 위상으로 정하고 기하로 교차검증한다. **불일치하면 중단**한다 |
| **차폐 후보를 미리 선별하지 않는다** | 광선마다 **전 면과 최근접 교차**를 판정한다 |
| **수렴은 AND 조건이다** | 온도 증분과 에너지 불균형을 **둘 다** 만족해야 수렴이다 |
| **검사를 끄는 스위치를 두지 않는다** | 중단하되 진단 파일은 끝까지 생성한다 |
| **근거 없는 상수를 도입하지 않는다** | 예: G4 허용오차는 고정값이 아니라 `64·n_elem·ε_machine` 으로 **항의 개수에서 유도**한다 |

## 재현성 — 실측 확인

`serial`, `mpi(1)`, `mpi(2)`, `mpi(4)` 의 절점 온도장이 **비트 단위로 완전히 일치**한다.

```
기준: serial   절점 435
  mpi n=1 : 비트 단위 일치 = True   최대차 0.000e+00
  mpi n=2 : 비트 단위 일치 = True   최대차 0.000e+00
  mpi n=4 : 비트 단위 일치 = True   최대차 0.000e+00
```

**이것이 가능한 이유** — 난수를 (세그먼트, 반사 횟수) 로 결정론적으로 정하고 광선
index 로 색인하며, 부분 결과를 **랭크 순서 그대로 배치**한다. 합산이 아니라 배치이므로
부동소수 덧셈 순서 문제가 발생하지 않는다.

**대가** — 각 프로세스가 전체 크기의 계수 행렬을 보유하므로 메모리가 프로세스 수에
비례해 늘어난다. 통신 최적화도 포기한다. 재현성을 택한 결과다.

## 설치와 새 컴퓨터에서의 실행

순수 Python 이며 컴파일할 것이 없다.

* **Python 3.11 이상** — NumPy·SciPy 면 된다.
* **Python 3.9 / 3.10** — 역시 동작하나 `pip install tomli` 가 필요하다. 문제
  파일이 TOML 이고, TOML 판독기가 표준 라이브러리에 들어온 것이 3.11 부터다.
  **macOS 는 Xcode 명령행 도구로 3.9 를 설치하므로**, 최신 Python 을 따로 깔지
  않았다면 Mac 에서는 이쪽이 보통이다.

Linux·macOS(Apple Silicon 포함)·Windows 에서 그대로 실행되도록 작성했다. 도면
스크립트는 한글 폰트를 자동으로 고르고, 없으면 조용히 기본 폰트로 물러난다.

```bash
pip install numpy scipy
pip install pytest     # 시험 실행 시
pip install mpi4py     # MPI 사용 시에만
export PYTHONPATH=src
```

## 실행

```bash
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
mpirun -n 4 python -m axirad2d.cli examples/bm2_bm5/case_bm2.toml   # parallel = "mpi"
bash run_all.sh        # 격자 → 시험 63건 → 벤치마크 → 해석해 대조
```

## 배포된 출력의 재현성

여기 커밋된 예제 출력은 장식이 아니다. 새 컴퓨터에서 **바이트 단위로** 다시 생성된다.
릴리스 압축본을 깨끗한 디렉터리 두 곳에 풀어 전부 다시 계산해 확인했다.

| 그대로 재생성되는 것 | 되지 않는 것 |
|---|---|
| 모든 격자 `.npz`, `results.npz`, `temperature.csv`, 참조값, 그리고 **도면 PNG** | `diagnostics.json` 의 `time_radiation_s`·`time_total_s` — 벽시계 시간이라 원리적으로 불가 |

직접 확인하는 법:

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5:examples/db3
python3 tools/check_reproducibility.py      # 끝에 REPRODUCIBLE 이 나온다
```

커밋된 출력을 옆에 치워 두고 다시 계산해 비트 단위로 비교하며, 제외하는 두 시간
항목을 감추지 않고 이름을 대고 밝힌다.

## 벤치마크

3종이며, **모든 참조값을 공개된 닫힌 형태 수식으로 직접 계산**했다. 어떤 문헌의
수치표도 복제하지 않았다.

| | BM-1 동축 원통 공동 | BM-2 유한 원통 공동 | BM-5 동심 구 |
|---|---|---|---|
| 면 | 평면·직선 | 평면·직선 | **곡면 (원뿔대 근사)** |
| 형상계수 | 자명 (0, 1) | **비자명 (0.1716)** | 자명 (0, 1) |
| 방사율 | 흑체벽에서 정확 | 전 흑체 | **회색 (정확)** |
| 정확해 근거 | 볼록체 완전 포위 | 닫힌 형태 수식 | 조사량 균일 (대칭성) |
| 정확해 대비 오차 | +0.0019 % / +0.0081 % | −0.041 % / +0.029 % | −0.035 % / +0.0320 % |
| Newton 반복 | 6 | 4 | 9 |
| 에너지 상대 잔차 | 1.1e-12 | 5.3e-15 | 5.7e-14 |

**대조 15항목 전부 정확해 대비 0.06 % 이내이며, 그중 8항목은 정확히 일치한다.**

문제 정의와 도면 — `docs/BENCHMARK_PROBLEMS.md`,
`figures/benchmark_definitions.png`
결과 도면 — `figures/results_temperature_fields.png`, `figures/results_verification_summary.png`
전체 표 — `docs/BENCHMARK_RESULTS.md`

**생체열 (v2.0).** Pennes 관류 항은 **대류가 아니라 체적 열원**이다. 이 코드
어디에도 속도장과 이류항이 없으므로, 조직 내부의 수송 기구는 여전히 전도뿐이다.
`docs/USER_GUIDE.md` 5a절 참조. 검증은 별도 모음 `yuchiri-axibio-bench` 의 벤치마크
**DB-3** 로 검증했다 — 최밀 격자 절점 L∞ 오차 7.4e-09 K, 관측 차수 3.90, 허위 반경
변화 2.8e-13 K. `examples/db3/` 참조.

### ⚠ 회색벽 2면 집중식을 검증 기준으로 쓰지 말 것

```
Q = σ(T₁⁴−T₂⁴) / [ (1−ε₁)/(ε₁A₁) + 1/(A₁F₁₂) + (1−ε₂)/(ε₂A₂) ]
```

이 식은 **각 면의 복사도가 균일**하다고 **추가로** 가정한다. 원통 공동벽은 부위마다
조사량이 다르므로 그 가정이 성립하지 않는다.

실측 — ε₂ = 0.6 일 때 본 구현과의 차이가 **약 1.6 %** 였고, 광선 수를
10,000 → 80,000 으로 늘려도 **줄지 않았다**(계통 편차). ε₂ = 1.0(가정 불필요)에서는
**0.005 %** 로 떨어졌다. 대칭성 때문에 조사량이 균일한 동심 구에서는 **0.035 %** 다.

**편차의 원인은 코드가 아니라 집중식 자체의 가정이다.** 이를 모르면 정상 코드를
1.6 % 틀렸다고 오판할 수 있다.

## 알려진 한계 — 결과를 믿기 전에 읽을 것

1. **절점 순환 이동, 중간절점 오배치, 절점 수 오기는 검출되지 않을 수 있다.**
   근거 없는 임계값을 도입하지 않기 위한 대가다.
2. **2차 요소의 중간절점은 복사 열유속을 받지 않는다.** 복사면은 코너 절점 2개로
   정의되는 직선 원뿔대다.
3. **전도와 복사가 서로 다른 형상을 본다** — 곡선 변 대 직선 근사.
4. **몬테카를로 통계 오차는 해에 그대로 반영되며 반복해도 줄지 않는다.**
   Gebhart 계수는 실행당 1회 계산한다. 광선 수를 바꿔 직접 확인하라.
5. **허용오차를 통계 잡음보다 작게 주면 항상 수렴 실패로 종료된다.**
6. **MPI 재현성을 위해 메모리를 프로세스 수에 비례해 사용한다.**
7. **투명 재료에도 0 이 아닌 작은 `k` 를 주어야 한다.** `k = 0` 이면 그 영역
   내부 절점의 방정식이 특이해진다. 그 영역에 그려지는 온도는 물리적 의미가 없다.

전문은 `DISCLAIMER.md` 참조.

## 문서

| 문서 | 내용 |
|---|---|
| `COPYRIGHT.md` | **저작권자 및 무료 공개 선언** |
| `DISCLAIMER.md` | **무보증 고지 — 사용 전 반드시 읽을 것** |
| `docs/USER_GUIDE.md` | 설치, 입력 형식, 실행, 진단 읽는 법, 중단 메시지 대처 |
| `docs/BENCHMARK_PROBLEMS.md` | **벤치마크 문제 정의, 도면, 정답, 출처** |
| `docs/BENCHMARK_RESULTS.md` | 정확해 대조 15항목 전체 표, 재현 방법 |
| `CONTRIBUTING.md` | 깨면 안 되는 설계 원칙 7가지 |
| `CHANGELOG.md` | 변경 이력 |

모든 문서는 영어·한국어 병기다.
**소스 코드의 주석과 실행 중 메시지는 한국어다.** 모든 중단 메시지의 영어 대역은
`docs/USER_GUIDE.md` 11장에 있다.

## 구현 현황

| 구현됨 | 미구현 |
|---|---|
| 요소 5종 (삼각형·혼합 격자 수렴 검증 완료) | 과도 해석 (후진 오일러) |
| **Pennes 관류 항과 대사 발열** (v2.0) | |
| 격자 검증 G1·G2·G4, 패치 시험, 비직교 기울기 시험 | |
| 복사면 자동 추출, 법선 교차검증 | Schur 정적 응축 |
| 몬테카를로 Gebhart, 누출 중단 | 상세 출력 일부 |
| 완전 결합 Newton, AND 수렴 조건 | |
| 경계조건 5종, TOML 입출력, 표준 진단 | |
| MPI 병렬 + 비트 단위 재현성 | |

## 모듈

```
src/axirad2d/
  elements.py    형상함수 5종, 수치적분
  mesh.py        격자, 위상, 검증 G1/G2/G4, 지문
  materials.py   온도 다항식 물성, 해석적 미분
  surfaces.py    복사면 자동 추출, enclosure, 법선 교차검증
  montecarlo.py  광선 추적, Gebhart 계수, 누출·상반성 진단
  assemble.py    경계조건, 전역 잔차·야코비안
  solve.py       Newton, 드라이버, MPI 결합
  problemio.py   TOML 입력, 결과·진단 출력
  cli.py         명령행
```

## AI 사용 고지

이 소프트웨어는 **Anthropic 의 Claude 를 도구로 사용하여 작성되었다.**

설계는 사람이 결정했다. 격자 입력 방식, 요소 종류, 복사면 추출 방식, 법선 판정과
불일치 시 처리, 경계조건 종류, 열원 입력, 연성 방식, 수렴 판정, 병렬 방식과
재현성 정책, 출력 수준 등 **20여 개의 설계 결정을 사람이 선택지 중에서 골랐고,
그 결정이 코드 구조를 규정한다.** 벤치마크 형상과 정확해의 선택, 그리고 회색벽
집중식이 검증 기준으로 부적합하다는 판단도 사람의 것이다.

Claude 는 그 결정을 코드와 시험으로 옮기는 데 사용되었다.

## 계보

본 코드에는 **어떤 장치의 형상 좌표도, 특정 재료의 물성 계수도, 특정 문제의
경계조건도 들어 있지 않다.** 형상·격자·물성·열원·경계조건이 전부 입력이다.

알고리즘은 전부 공지 기술이다 — Galerkin 유한요소법, 등매개 요소, Gauss 구적,
Gebhart 흡수계수, 몬테카를로 광선 추적, Newton–Raphson, 후진 오일러.

벤치마크 참조값은 공개된 수식으로 **직접 계산**하며, 어떤 수치표도 복제하지 않는다.

## 라이선스

MIT. `LICENSE` 참조. Copyright (c) 2026 **원유철 (Yoo Cheol WON)**.
어떠한 대가도 없이 무상 공개한다 — `COPYRIGHT.md` 참조.

> **명칭에 관하여.** "MIT 라이선스" 는 표준 허가형 라이선스 양식의 관용적
> 명칭이다. **매사추세츠 공과대학교와 어떠한 관련도 없으며 그 기관의 승인을
> 뜻하지도 않는다.** 본 소프트웨어의 저작권자는 원유철이다.

## 인용

`CITATION.cff` 참조.
