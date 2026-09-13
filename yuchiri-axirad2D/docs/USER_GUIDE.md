# yuchiri-axirad2D User Guide / 사용설명서

Version 0.1.0 · specification v1.1

> Read `DISCLAIMER.md` before use. / 사용 전 `DISCLAIMER.md` 를 읽으십시오.

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## Contents

1. Install · 2. Five-minute example · 3. Problem file (TOML) · 4. Mesh file
· 5. Materials · 6. Boundary conditions · 7. Heat sources · 8. Radiation
· 9. Solver and parallel · 10. Output and diagnostics · 11. Abort messages
· 12. Common mistakes

---

## 1. Install

```bash
git clone <repository>
cd yuchiri-axirad2D
pip install numpy scipy
pip install pytest            # to run tests
pip install mpi4py            # only for MPI
export PYTHONPATH=src
bash run_all.sh               # meshes -> 63 tests -> benchmarks -> comparison
```

## 2. Five-minute example

```bash
export PYTHONPATH=src
python examples/coaxial_enclosure/build_mesh.py
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python examples/coaxial_enclosure/reference.py
```

Output appears in `examples/coaxial_enclosure/out/`.

## 3. Problem file (TOML)

Input is split into a **problem file** and a **mesh file**; the problem file
points to the mesh.

```toml
schema_version = "1.0"
mesh_file      = "case.mesh.npz"    # relative to the problem file
mesh_hash      = "37fdbddf..."      # optional; mismatch aborts
length_unit    = 1.0                # multiplier on mesh coordinates; 1.0e-3 for mm

[analysis]
mode     = "steady"                 # only "steady" is supported at present
parallel = "serial"                 # "serial" | "mpi"

[material.<name>]  ...              # §5
[bc.<name>]        ...              # §6
[radiation]        ...              # §8
[solver]           ...              # §9
[output]
detail = false                      # true adds detailed output (§10)
```

### Mesh fingerprint (`mesh_hash`)

If the mesh and the problem file do not match, **boundary conditions land in the
wrong place and the run proceeds silently.** This guards against that.

* If `mesh_hash` is present the code compares it and **aborts** on mismatch.
* If absent, the computed fingerprint is written to the diagnostics. Copy it in.

**Change the mesh, change the hash.** Forgetting aborts, which is safe.

## 4. Mesh file

**This code does not generate meshes.** The mesh comes entirely from outside.

### 4.1 NPZ format

Read and written by `axirad2d.mesh.save_npz` / `load_npz`.

| Key | Shape | Contents |
|---|---|---|
| `nodes` | (nn, 2) | `(r, z)`. **`r >= 0`** |
| `elem_flat`, `elem_offset` | — | Connectivity, flattened (element lengths differ) |
| `elem_material` | (ne,) | Name from `[material.*]` |
| `elem_qvol` | (ne,) | Volumetric heat generation [W/m³] |
| `nset__<name>` | (k,) | Node set |

```python
from axirad2d.mesh import Mesh, save_npz
m = Mesh(nodes, elems, emat, qvol, {"outer_wall": outer_node_ids})
print(m.fingerprint())          # value for mesh_hash
save_npz("case.mesh.npz", m)
```

### 4.2 Five element types — identified by node count

| Nodes | Element | Order | Edges |
|---|---|---|---|
| 3 | triangle | linear | 3 |
| 4 | quadrilateral | linear | 4 |
| 6 | triangle | quadratic | 3 |
| 8 | quadrilateral, serendipity | quadratic | 4 |
| 9 | quadrilateral, Lagrange | quadratic | 4 |

**Five types may be mixed within one mesh.**

### 4.3 ★ Local node ordering — counter-clockwise, corners first

**Getting this wrong can produce a silently incorrect answer.** It is the most
common error.

```
6-node triangle                  8/9-node quadrilateral
      2                              3 - 6 - 2
      | \                            |       |
      5   4                          7  (8)  5
      |     \                        |       |
      0 - 3 - 1                      0 - 4 - 1
```

* Corners first, **counter-clockwise**.
* Then mid-side nodes **in edge order**. Edge `e` joins corner `e` to corner
  `(e+1) mod nc`.
* The centre node of the 9-node element is last (index 8).

### 4.4 Mesh checks — must pass before the solve starts

| Check | Content | Catches |
|---|---|---|
| **G1** | `det J > 0` at every integration point of every element | inverted, tangled, degenerate elements |
| **G2** | Sign of the corner-polygon area | some corner-ordering errors |
| **G4** | Element volume sum = divergence-theorem surface integral | connectivity errors, overlaps, gaps, 2π convention errors |

The tolerance is not a fixed constant but `64 × n_elem × ε_machine`,
**derived from the number of terms**.

> **The mid-side position check (G3) is deliberately absent**, to avoid an
> unjustified threshold. The price is that **cyclic node rotation and wrong node
> counts may go undetected.**

## 5. Materials

```toml
[material.graphite]
opaque     = true
emissivity = 0.85              # required when opaque = true
k_pos      = [5.0, 2.0e-3]     # k = 5.0 + 2e-3 * T
k_neg      = { 1 = 300.0 }     # + 300 / T
rho_pos    = [1800.0]          # for transient (not implemented yet)
cp_pos     = [710.0]
T_range    = [200.0, 3000.0]   # optional; excursions are reported, not fatal

[material.argon]
opaque = false                 # transparent to radiation
k_pos  = [1.0e-5]
```

Unified form:

```
f(T) = Σ_{p≥0} c_p T^p  +  Σ_{n≥1} d_n / T^n         [SI]
```

* **Depends on temperature only.** Isotropic; no position or direction dependence.
* `df/dT` is differentiated **analytically** term by term and enters the Newton
  Jacobian.
* `opaque = false` means **transparent to radiation**; conduction is still solved.
* **If the `k` actually used is ≤ 0 the run aborts immediately.**

> **Do not give a transparent material `k = 0`.** The equations for interior
> nodes of that region become singular. The examples use `1e-5 W/(m·K)`.
> Temperatures plotted in that region have no physical meaning.

## 5a. Bioheat: perfusion and metabolic heat (v2.0)

```toml
[blood]                       # properties of BLOOD, not of a tissue
rho_cb     = 3.99622e6        # blood volumetric heat capacity [J/(m^3 K)]
T_arterial = 310.15           # arterial temperature [K]

[material.dermis]
opaque     = true
emissivity = 0.98
k_pos      = [0.37]
perfusion  = 0.038            # omega_b [1/s], per unit tissue volume
q_met      = 368.1            # metabolic heat generation [W/m^3]
```

Blood properties sit at problem level because they are properties of blood, the
same for every tissue in one body; duplicating them per material would let them
disagree. **Asking for perfusion without a `[blood]` section aborts** — treating
the sink as zero would silently delete most of the energy path.

The added term is a volumetric source, positive when blood is warmer than tissue:

```
+ omega_b * rho_b * c_b * ( T_arterial - T )        [W/m^3]
```

Its strength relative to conduction over a length `L` is the dimensionless group

```
kappa = sqrt( omega_b rho_b c_b / k )      (kappa L)^2 = perfusion / conduction
```

`1/kappa` is the **thermal penetration depth**: how far a disturbance reaches
before blood carries it away.

### ★ What this term is, and what it is not

**It is not convection.** There is no velocity field and no advection term
`v · grad T` anywhere in this code. The Pennes term is a *lumped* stand-in for
blood–tissue heat exchange: blood is assumed to arrive at `T_arterial`, come
fully into thermal equilibrium with the local tissue, and leave at the local
temperature. The model has no idea which way the blood is flowing.

Within the tissue, therefore, **conduction is the only transport mechanism in
this code**; perfusion is a distributed source that feeds it. In the DB-3
benchmark the conduction flux grows from 2.8 W/m² at the core boundary to
137.8 W/m² at the surface precisely because perfusion keeps adding to it along
the way.

Not represented, and out of scope:

| Not represented | Consequence |
|---|---|
| advection `v · grad T`, and any velocity field | blood flow has no direction |
| large vessels | no local effect of an artery or a vein |
| counter-current artery–vein exchange | the effect Weinbaum–Jiji type models add |
| temperature-dependent perfusion `omega(T)` | no feedback of heating on blood flow — which matters in hyperthermia and ablation |
| **mass transfer of any kind** | **no evaporative cooling.** A surface can lose heat here only by convection and radiation; sweating and insensible perspiration are not modelled |

The Pennes equation is a modelling hypothesis, not a law. See `DISCLAIMER.md`.

**Where to get tissue property values.** Not from the examples in this
repository: those are benchmark coefficients, fixed so that a reference solution
is reproducible, not best estimates of anyone's tissue. For realistic values with
documented spread use the IT'IS database — Baumgartner et al., *IT'IS Database
for thermal and electromagnetic parameters of biological tissues*, Version 5.0,
DOI 10.13099/VIP21000-05-0, `itis.swiss/database`.


## 6. Boundary conditions

Boundary conditions attach to **node sets**. Sign convention: **inward is positive.**

```toml
[bc.outer]
type = "dirichlet"
nset = "outer_wall"
T    = 300.0

[bc.side]
type = "flux"
nset = "side_face"
q    = -1500.0          # negative = heat leaving

[bc.top]
type = "convection"
nset = "top_face"
h     = 25.0
T_inf = 300.0

[bc.shell]
type = "env_radiation"
nset = "shell_outside"
emissivity = 0.9
T_env      = 300.0
```

| type | Expression | Note |
|---|---|---|
| `dirichlet` | `T = T0` | Without one the solution may not be unique (warning) |
| `flux` | `q_in = q` | |
| `adiabatic` | `q_in = 0` | **Holds automatically**; need not be specified |
| `convection` | `q_in = h (T_inf − T)` | |
| `env_radiation` | `q_in = ε σ (T_env⁴ − T⁴)` | Nonlinear; `4εσT³` in the Jacobian |

### 6.1 ★ How the integration edges are chosen

Flux, convection and environment radiation need a surface integral. The target is

> **boundary edges all of whose nodes belong to the node set.**

* **For quadratic elements the mid-side node must also be in the set.** Corners
  alone will not select the edge.
* **Omit one node and that edge's flux disappears without an error.**
  To let you catch this, the diagnostics **always** report the number of extracted
  edges and their total area per node set. Check them against your intent.

### 6.2 The symmetry axis

`r = 0` is a **natural boundary condition**: the `2πr` weight vanishes, so
adiabatic holds with no action. **Do not apply a boundary condition on the axis.**

### 6.3 ★ Environment radiation overlapping an automatic radiating surface

| Combination | Verdict |
|---|---|
| Dirichlet face + automatic radiating surface | **Normal.** Allowed |
| **Environment radiation face + automatic radiating surface** | **Abort.** Energy would be double counted |

There is no switch to disable this.

## 7. Heat sources

**Element-wise volumetric heat generation `q_vol` [W/m³]** in the mesh file.

Total power is a result, not an input:

```
P_total = Σ_e q_vol,e × V_e ,    V_e = ∫ 2πr dA
```

It appears in the diagnostics as `power.source`; compare it against your intent.

> Per-element-set total power input is not provided. To specify a total in W,
> convert yourself: `q_vol = P / V` (see the examples).

## 8. Radiation

```toml
[radiation]
n_ray                = 40000     # rays per segment
seed                 = 12345
n_bounce_max         = 20
leak_tol             = 1.0e-5
boundary_emissivity  = 1.0       # edges where a transparent element meets the domain boundary
```

### 8.1 Radiating surfaces are found automatically

You do not supply a list. The code

1. computes edge-sharing topology,
2. takes as radiating surfaces the edges **between a transparent and an opaque
   element**, and the **boundary edges of transparent elements**,
3. decomposes the **connected components of transparent elements**, each becoming
   one enclosure.

**The enclosure count is not hard-coded.**

### 8.2 Normals — two independent determinations; mismatch aborts

* Primary: **element adjacency** (topological) — the side where the transparent
  element lies.
* Cross-check: **direction to the element centroid** (geometric).

If even one segment disagrees, the run **aborts without producing a solution**,
after writing segment ids, coordinates, element ids and both normal vectors to
the diagnostics. **There is no switch.**

### 8.3 Leakage — never corrected

If `Σ_b B_ab` falls short of 1 it is **not padded to 1.** Leakage is counted by cause.

| Cause | Meaning |
|---|---|
| Open-geometry leakage | A ray hit no surface. **The enclosure is not closed** |
| Bounce-limit leakage | Emissivity so low that absorption did not occur within `n_bounce_max` |

If either exceeds `leak_tol`, the run **aborts**.

### 8.4 Gebhart factors are computed once per run

They depend only on geometry and emissivity, so they are reused across all Newton
iterations. This is why the residual decreases deterministically and **quadratic
convergence is observable.**

**The cost** — the statistical error of the factors is carried into the solution
and does not shrink with iteration. **Double and quadruple the ray count and
check the result does not move.**

## 9. Solver and parallel

```toml
[solver]
T_init    = 400.0
eps_T     = 1.0e-9      # max|dT| / temperature span
eps_E     = 1.0e-9      # relative energy imbalance
max_iter  = 40
quad_bump = 0           # raise the quadrature order (convergence checking)
```

### 9.1 Convergence is an AND condition

**Both** the increment and the energy imbalance must be satisfied. One alone is
not accepted.

There is no stagnation detection (that would need an unjustified threshold), so
**tolerances tighter than the Monte Carlo noise always end in failure.** Even on
failure the diagnostics and the last temperature field are written.

### 9.2 Parallel

```bash
# with analysis.parallel = "mpi"
mpirun -n 4 python -m axirad2d.cli case.toml
```

**Serial and MPI results are bit-for-bit identical**, and independent of process
count, because random numbers are deterministic in (segment, bounce) and partial
results are **placed** in rank order rather than summed.

Without `mpi4py`, `serial` still works; but **if you ask for `mpi` and the import
fails the run aborts.** It never falls back silently.

## 10. Output and diagnostics

| File | Contents |
|---|---|
| `out/temperature.csv` | `(node_id, r, z, T)` per node |
| `out/results.npz` | temperature field; segment geometry, area, emissivity, temperature |
| `out/diagnostics.json` | mesh checks, radiation diagnostics, energy balance, convergence history |

Standard diagnostics are **always** written. There is no switch.

### 10.1 Five things to check every time

| # | Item | Normal | If not |
|---|---|---|---|
| 1 | **Energy-balance relative residual** | ~1e-12 or below | **Something is wrong. Do not use the result** |
| 2 | **Leakage** (open / bounce) | 0 or very small | The enclosure is leaking |
| 3 | **Closure `Σ B_ab`** | very close to 1 | Same cause as above |
| 4 | **Edges and total area per node set** | as intended | You omitted a node (§6.1) |
| 5 | **Convergence status** | success | On failure the result is not a solution |

The diagnostics also record the **random seed, maximum bounce count and
`leak_tol`**, so a result file states exactly what produced it.

### 10.2 Three reciprocity metrics

All threshold-free.

| Metric | Behaviour |
|---|---|
| `max_rel` | Strictest, but **saturates at 1.0 when there are many segments** |
| `max_abs` | Scale-normalised; does not saturate |
| `l1` | Global; **must decrease as `N^(−1/2)`** with ray count |

If `l1` does not fall as `N^(−1/2)`, something other than statistics is at work.

### 10.3 Detailed output

`[output] detail = true` adds three arrays to `results.npz`:

| Array | Size | Contents |
|---|---|---|
| `gebhart_B` | segments² | the full Gebhart absorption matrix — **use with care** |
| `segment_net_flux` | segments | net radiative flux per segment [W/m²], inward positive |
| `nodal_residual` | nodes | the residual at the converged solution; non-zero only at Dirichlet nodes, where it is the reaction |

Nothing else is added. Element-wise flux vectors and per-iteration temperature
fields are **not** implemented.

## 11. Abort messages (Korean message → meaning)

Runtime messages are in Korean. Their meanings:

| Korean message | Meaning | What to do |
|---|---|---|
| `G1 위반 — 야코비안이 양수가 아닌 요소` | G1 violated: non-positive Jacobian | Fix the element listed in the diagnostics |
| `G2 위반 — 코너 서명 면적이 양수가 아님` | G2 violated: non-positive signed corner area | Check the counter-clockwise convention (§4.3) |
| `G4 위반 — 부피 상대차` | G4 violated: volume mismatch | Check `duplicate_nodes` first; then connectivity |
| `§10.4 법선 교차검증 실패` | Normal cross-check failed | See `normal_mismatch`. **There is no way to disable it** |
| `§10.7 누출 검사 실패` | Leakage check failed | Open leakage → mesh; bounce leakage → `n_bounce_max` |
| `§8.5 위반 — 환경 복사가 자동 복사면과 겹침` | Environment radiation overlaps an automatic radiating surface | Remove environment radiation from that node set |
| `재료 ... 의 열전도도가 0 이하` | Conductivity ≤ 0 for that material | Check the coefficients and `T_range` |
| `격자 지문 불일치` | Mesh fingerprint mismatch | Recompute and update `mesh_hash` |
| `최대 반복 ... 에서 수렴하지 않았다` | Did not converge within `max_iter` | Increase rays, or set a realistic `eps_E` |
| `지원하지 않는 요소 절점 수` | Unsupported node count | Only 3, 4, 6, 8, 9 are supported |
| `절점 집합 '...' 이 격자에 없다` | Node set not found in the mesh | Check the name |

**Every abort writes the diagnostics file to completion.** "It stopped and I have
no idea why" should never happen.

## 12. Common mistakes

1. **Mid-side nodes of quadratic elements not included in the node set** → the
   boundary condition is not applied to that edge. Check the extracted edge count.
2. **`k = 0` for a transparent material** → singular matrix. Use a small value.
3. **Mesh changed but `mesh_hash` not updated** → aborts (intended).
4. **Trusting a single ray count** → double and quadruple it.
5. **Forgetting `length_unit`** → a mm mesh read as m is off by 10⁹ in volume.
   Check the total volume in the diagnostics.
6. **Using the lumped two-surface gray formula to verify** → it assumes uniform
   radiosity and fails for general geometry. See `docs/BENCHMARK_RESULTS.md` §7.
7. **Applying an adiabatic condition on the axis** → unnecessary; harmless but
   meaningless.

---
---

# 한국어

버전 0.1.0 · 사양서 v1.1

> 사용 전 `DISCLAIMER.md` 를 반드시 읽으십시오.

---

## 목차

1. [설치](#1-설치)
2. [5분 예제](#2-5분-예제)
3. [입력 — 문제 파일 (TOML)](#3-입력--문제-파일-toml)
4. [입력 — 격자 파일](#4-입력--격자-파일)
5. [물성](#5-물성)
6. [경계조건](#6-경계조건)
7. [열원](#7-열원)
8. [복사](#8-복사)
9. [해법과 병렬](#9-해법과-병렬)
10. [출력과 진단 읽는 법](#10-출력과-진단-읽는-법)
11. [중단 메시지와 대처](#11-중단-메시지와-대처)
12. [자주 하는 실수](#12-자주-하는-실수)

---

## 1. 설치

```bash
git clone <저장소 주소>
cd yuchiri-axirad2D
pip install numpy scipy
pip install pytest            # 시험 실행 시
pip install mpi4py            # MPI 사용 시에만
export PYTHONPATH=src
```

동작 확인:

```bash
bash run_all.sh               # 격자 생성 -> 시험 63건 -> 벤치마크 -> 해석해 대조
```

---

## 2. 5분 예제

```bash
export PYTHONPATH=src
python examples/coaxial_enclosure/build_mesh.py          # 격자 생성
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python examples/coaxial_enclosure/reference.py           # 해석해와 대조
```

출력은 `examples/coaxial_enclosure/out/` 에 생긴다.

---

## 3. 입력 — 문제 파일 (TOML)

입력은 **문제 파일**과 **격자 파일** 두 개로 나뉜다. 문제 파일이 격자 파일을 가리킨다.

```toml
schema_version = "1.0"
mesh_file      = "case.mesh.npz"    # 문제 파일 기준 상대경로
mesh_hash      = "37fdbddf..."      # 선택. 있으면 대조하고 불일치 시 중단
length_unit    = 1.0                # 격자 좌표에 곱할 인자. mm 격자면 1.0e-3

[analysis]
mode     = "steady"                 # 현재 "steady" 만 지원
parallel = "serial"                 # "serial" | "mpi"

[material.<이름>]  ...              # 5절
[bc.<이름>]        ...              # 6절
[radiation]        ...              # 8절
[solver]           ...              # 9절
[output]
detail = false                      # true 이면 상세 출력 (10절)
```

### 격자 지문 (`mesh_hash`)

격자와 문제 파일의 짝이 어긋나면 **경계조건이 엉뚱한 곳에 걸린 채 조용히 계산된다.**
이를 막기 위한 장치다.

* `mesh_hash` 를 적어 두면 코드가 대조하고, 불일치 시 **중단**한다.
* 적지 않으면 코드가 계산한 지문을 진단에 출력한다. 그것을 복사해 넣어 고정하라.

**격자를 바꾸면 지문도 바꿔야 한다.** 잊으면 중단되므로 안전하다.

---

## 4. 입력 — 격자 파일

**이 코드는 격자를 만들지 않는다.** 격자는 전량 외부에서 온다.

### 4.1 NPZ 형식

`axirad2d.mesh.save_npz` / `load_npz` 가 읽고 쓴다. 담기는 배열:

| 키 | 형상 | 내용 |
|---|---|---|
| `nodes` | (nn, 2) | `(r, z)`. **`r >= 0`** |
| `elem_flat`, `elem_offset` | — | 요소 연결. 요소마다 길이가 달라 평탄화해 저장 |
| `elem_material` | (ne,) | `[material.*]` 의 이름 |
| `elem_qvol` | (ne,) | 체적 발열률 [W/m³] |
| `nset__<이름>` | (k,) | 절점 집합 |

파이썬에서 직접 만드는 예:

```python
from axirad2d.mesh import Mesh, save_npz
m = Mesh(nodes, elems, emat, qvol, {"outer_wall": outer_node_ids})
print(m.fingerprint())          # mesh_hash 에 넣을 값
save_npz("case.mesh.npz", m)
```

### 4.2 지원 요소 5종 — 절점 수로 판별

| 절점 수 | 요소 | 차수 | 변 |
|---|---|---|---|
| 3 | 삼각형 | 1차 | 3 |
| 4 | 사각형 | 1차 | 4 |
| 6 | 삼각형 | 2차 | 3 |
| 8 | 사각형 Serendipity | 2차 | 4 |
| 9 | 사각형 Lagrange | 2차 | 4 |

**한 격자에 5종이 섞여도 된다.**

### 4.3 ★ 국소 절점 순서 — 반시계, 코너 먼저

**이것이 틀리면 조용히 잘못된 답이 나올 수 있다.** 가장 흔한 오류다.

```
삼각형 6절점                     사각형 8·9절점
      2                              3 - 6 - 2
      | \                            |       |
      5   4                          7  (8)  5
      |     \                        |       |
      0 - 3 - 1                      0 - 4 - 1
```

* 코너를 **반시계 방향**으로 먼저 적는다.
* 그다음 중간절점을 **변 순서대로** 적는다. 변 `e` 는 코너 `e` 와 코너 `(e+1) mod nc` 를 잇는다.
* 9절점의 중심 절점은 마지막(index 8).

### 4.4 격자 검증 — 통과해야 계산이 시작된다

| 검사 | 내용 | 잡는 것 |
|---|---|---|
| **G1** | 전 요소·전 적분점 `det J > 0` | 뒤집힌 요소, 꼬인 요소, 퇴화 요소 |
| **G2** | 코너 다각형 면적의 부호 | 코너 순서 오류 일부 |
| **G4** | 요소 부피 합 = 발산정리 표면적분 | 연결 오류, 겹침, 빈틈, 2π 규약 오류 |

허용오차는 고정 상수가 아니라 `64 × 요소수 × 기계정밀도` 로 **항의 개수에서 유도**한다.

> **G3(중간절점 위치)은 일부러 두지 않았다.** 근거 없는 임계값을 도입하지 않기
> 위해서다. 그 대가로 **절점 순환 이동과 절점 수 오기는 검출되지 않을 수 있다.**

---

## 5. 물성

```toml
[material.graphite]
opaque     = true
emissivity = 0.85              # opaque = true 이면 필수
k_pos      = [5.0, 2.0e-3]     # k = 5.0 + 2e-3 * T
k_neg      = { 1 = 300.0 }     # + 300 / T
rho_pos    = [1800.0]          # 과도 해석용 (현재 미구현)
cp_pos     = [710.0]
T_range    = [200.0, 3000.0]   # 선택. 벗어나면 진단에 보고 (중단하지 않음)

[material.argon]
opaque = false                 # 복사에 투명
k_pos  = [1.0e-5]
```

통일 형태:

```
f(T) = Σ_{p≥0} c_p T^p  +  Σ_{n≥1} d_n / T^n         [SI]
```

* **온도에만 의존한다.** 등방이며 위치·방향 의존이 없다.
* 미분 `df/dT` 는 항별로 **해석적으로** 계산되어 Newton 야코비안에 들어간다.
* `opaque = false` 는 **복사에 투명**하다는 뜻이다. 전도는 정상적으로 계산된다.
* **실제로 쓰인 `k` 가 0 이하이면 즉시 중단한다.**

> **투명 재료에 `k = 0` 을 주지 말 것.** 그 영역 내부 절점의 방정식이 특이해진다.
> 예제는 `1e-5 W/(m·K)` 를 쓴다. 그 영역에 그려지는 온도는 물리적 의미가 없다.

---

## 5a. 생체열: 관류와 대사 발열 (v2.0)

```toml
[blood]                       # 조직이 아니라 '혈액' 의 성질
rho_cb     = 3.99622e6        # 혈액 체적 열용량 [J/(m^3 K)]
T_arterial = 310.15           # 동맥혈 온도 [K]

[material.dermis]
opaque     = true
emissivity = 0.98
k_pos      = [0.37]
perfusion  = 0.038            # omega_b [1/s], 조직 단위 체적당
q_met      = 368.1            # 대사 발열 [W/m^3]
```

혈액 물성은 문제 수준에 둔다. 혈액의 성질이며 한 개체 안에서 모든 조직에 대해 같은
값인데, 재료마다 복제하면 서로 어긋날 수 있기 때문이다. **`[blood]` 절 없이 관류를
요청하면 중단한다** — 열싱크를 조용히 0 으로 두면 에너지 경로의 대부분이 사라진다.

추가되는 항은 체적 열원이며, 혈액이 조직보다 따뜻하면 양수다.

```
+ omega_b * rho_b * c_b * ( T_arterial - T )        [W/m^3]
```

길이 `L` 에 대한 전도 대비 세기는 무차원 수로 나타난다.

```
kappa = sqrt( omega_b rho_b c_b / k )      (kappa L)^2 = 관류 / 전도
```

`1/kappa` 가 **열침투깊이**다. 교란이 혈액에 실려 나가기 전에 도달하는 거리다.

### ★ 이 항이 무엇이고 무엇이 아닌가

**대류가 아니다.** 이 코드 어디에도 속도장이 없고 이류항 `v · grad T` 가 없다.
Pennes 항은 혈액–조직 열교환을 **뭉뚱그린 대역(lumped)** 이다. 혈액이
`T_arterial` 로 들어와 국소 조직과 완전히 열평형에 이른 뒤 국소 온도로 나간다고
가정한다. **모델은 혈액이 어느 쪽으로 흐르는지 알지 못한다.**

따라서 조직 내부에서 **이 코드의 수송 기구는 전도뿐**이며, 관류는 그것에 열을 부어
넣는 분산 공급원이다. DB-3 벤치마크에서 전도 유속이 심부 경계의 2.8 W/m² 에서
표면의 137.8 W/m² 로 커지는 것이 바로 그 때문이다.

표현되지 않은 것, 범위 밖:

| 없는 것 | 결과 |
|---|---|
| 이류항 `v · grad T` 와 속도장 | 혈류에 방향이 없다 |
| 대혈관 | 동맥·정맥의 국소 효과가 없다 |
| 동맥–정맥 역류 열교환 | Weinbaum–Jiji 계열 모델이 더하는 효과 |
| 온도 의존 관류 `omega(T)` | 가열이 혈류를 바꾸는 되먹임이 없다 — 온열치료·소작에서 중요하다 |
| **물질전달 일체** | **증발 냉각이 없다.** 이 코드에서 표면은 대류와 복사로만 열을 잃는다. 땀과 무감성 발한은 모델링되지 않는다 |

Pennes 식은 법칙이 아니라 모델 가설이다. `DISCLAIMER.md` 참조.

**조직 물성값은 어디서 가져올 것인가.** 이 저장소의 예제에서 가져오지 말 것. 그것은
참조해가 재현되도록 고정한 **벤치마크 계수**이지 누군가의 조직에 대한 최선 추정치가
아니다. 변동까지 문서화된 현실적 값이 필요하면 IT'IS 데이터베이스를 쓰라 —
Baumgartner 외, Version 5.0, DOI 10.13099/VIP21000-05-0, `itis.swiss/database`.


## 6. 경계조건

경계조건은 격자의 **절점 집합**에 건다. 부호 규약은 **영역 안으로 들어오는 것이 양(+)**.

```toml
[bc.outer]
type = "dirichlet"
nset = "outer_wall"
T    = 300.0

[bc.side]
type = "flux"
nset = "side_face"
q    = -1500.0          # 음수 = 열이 나감

[bc.top]
type = "convection"
nset = "top_face"
h     = 25.0
T_inf = 300.0

[bc.shell]
type = "env_radiation"
nset = "shell_outside"
emissivity = 0.9
T_env      = 300.0
```

| type | 수식 | 비고 |
|---|---|---|
| `dirichlet` | `T = T0` | 없으면 해가 유일하지 않을 수 있다 (경고) |
| `flux` | `q_in = q` | |
| `adiabatic` | `q_in = 0` | **적지 않아도 자동 성립** (자연 경계조건) |
| `convection` | `q_in = h (T_inf − T)` | |
| `env_radiation` | `q_in = ε σ (T_env⁴ − T⁴)` | 비선형. 야코비안에 `4εσT³` |

### 6.1 ★ 면적분 대상 변의 결정

열유속·대류·환경 복사는 면적분이 필요하다. 대상은

> **외곽 변 중, 그 변의 모든 절점이 해당 절점 집합에 속하는 변**

* **2차 요소는 중간절점도 집합에 넣어야 한다.** 코너만 넣으면 그 변은 선택되지 않는다.
* **절점을 하나 빠뜨리면 그 변의 유속이 에러 없이 사라진다.**
  이를 확인하려고 진단에 **집합별 추출 변 개수와 총면적**을 항상 출력한다. 반드시 대조하라.

### 6.2 대칭축

`r = 0` 은 **자연 경계조건**이다. `2πr` 가중치가 0 이므로 아무것도 하지 않아도
단열이 성립한다. **대칭축에 경계조건을 주지 말 것.**

### 6.3 ★ 환경 복사와 자동 복사면의 중첩

| 조합 | 판정 |
|---|---|
| Dirichlet 면 + 자동 복사면 | **정상.** 허용 |
| **환경 복사 면 + 자동 복사면** | **중단.** 에너지가 이중 계산된다 |

끄는 스위치는 없다.

---

## 7. 열원

**요소별 체적 발열률 `q_vol` [W/m³]** 을 격자 파일에 담는다.

총 투입 전력은 입력이 아니라 계산 결과다.

```
P_total = Σ_e q_vol,e × V_e ,    V_e = ∫ 2πr dA
```

진단의 `power.source` 로 출력되므로, 의도한 값과 대조하라.

> 요소 집합별 총 전력 입력은 제공하지 않는다. 총 W 를 넣고 싶으면
> `q_vol = P / V` 로 직접 환산하라 (예제 참조).

---

## 8. 복사

```toml
[radiation]
n_ray                = 40000     # 세그먼트당 광선 수
seed                 = 12345
n_bounce_max         = 20
leak_tol             = 1.0e-5
boundary_emissivity  = 1.0       # 투명 요소가 도메인 경계와 접하는 변
```

### 8.1 복사면은 자동으로 찾는다

사용자가 복사면 목록을 주지 않는다. 코드가

1. 요소 변의 공유 관계를 계산하고,
2. **투명 요소와 불투명 요소가 만나는 변** 및 **투명 요소의 외곽 변**을 복사면으로 삼고,
3. **투명 요소의 연결 성분**을 분해해 각각을 하나의 enclosure 로 만든다.

**enclosure 개수는 하드코딩되지 않는다.** 격자에서 나오는 대로 몇 개든 만든다.

### 8.2 법선 — 두 방법으로 판정하고 불일치하면 중단

* 1차: **요소 인접 관계**(위상). 투명 요소가 있는 쪽.
* 2차: **요소 중심 방향**(기하).

두 판정이 어긋나는 세그먼트가 하나라도 있으면 **해를 내놓지 않고 중단**한다.
단 진단 파일에 세그먼트 번호·좌표·요소 번호·두 법선 벡터를 남긴다. **끄는 스위치는 없다.**

### 8.3 누출 — 보정하지 않는다

`Σ_b B_ab` 가 1 에 미달해도 **1 로 채우지 않는다.** 누출은 원인별로 계수한다.

| 원인 | 뜻 |
|---|---|
| 열린 형상 누출 | 광선이 어느 면과도 교차하지 못했다. **enclosure 가 닫혀 있지 않다** |
| 반사 횟수 초과 | 방사율이 매우 낮아 `n_bounce_max` 안에 흡수되지 않았다 |

둘 중 하나라도 `leak_tol` 을 넘으면 **중단한다.**

### 8.4 Gebhart 계수는 실행당 1회

형상과 방사율에만 의존하므로 Newton 반복 전체에서 재사용한다.
그래서 잔차가 결정론적으로 감소하고 **2차 수렴이 관측된다.**

**대가** — 계수의 통계 오차는 해에 그대로 실리며 반복해도 줄지 않는다.
**광선 수를 2배·4배로 바꿔 결과가 변하지 않는지 직접 확인하라.**

---

## 9. 해법과 병렬

```toml
[solver]
T_init    = 400.0
eps_T     = 1.0e-9      # max|dT| / 온도범위
eps_E     = 1.0e-9      # 에너지 불균형 상대값
max_iter  = 40
quad_bump = 0           # 적분 차수를 올린다 (수렴 확인용)
```

### 9.1 수렴은 AND 조건

**증분과 에너지 불균형을 둘 다** 만족해야 수렴이다. 한쪽만으로는 인정하지 않는다.

정체 검출은 두지 않는다(근거 없는 임계값을 배제). 그래서 **허용오차를 몬테카를로
통계 잡음보다 작게 주면 항상 실패로 종료된다.** 실패해도 진단과 마지막 온도장은 남는다.

### 9.2 병렬

```bash
# analysis.parallel = "mpi" 로 두고
mpirun -n 4 python -m axirad2d.cli case.toml
```

**직렬과 MPI 결과가 비트 단위로 같다.** 프로세스 수를 바꿔도 같다.
난수를 (세그먼트, 반사 횟수)로 결정론적으로 정하고, 부분 결과를 랭크 순서대로
**배치**하기 때문이다(합산이 아니므로 덧셈 순서 문제가 없다).

`mpi4py` 가 없으면 `serial` 은 정상 동작하지만, **`mpi` 를 명시했는데 임포트가
실패하면 중단한다.** 조용히 직렬로 떨어지지 않는다.

---

## 10. 출력과 진단 읽는 법

| 파일 | 내용 |
|---|---|
| `out/temperature.csv` | 절점별 `(node_id, r, z, T)` |
| `out/results.npz` | 온도장, 세그먼트 기하·면적·방사율·온도 |
| `out/diagnostics.json` | 격자 검증, 복사 진단, 에너지 수지, 수렴 이력 전체 |

표준 진단은 **항상** 출력된다. 끄는 스위치는 없다.

### 10.1 반드시 확인할 5가지

| # | 항목 | 정상 | 어긋나면 |
|---|---|---|---|
| 1 | **에너지 수지 상대 잔차** | ~1e-12 이하 | **어딘가 틀렸다.** 결과를 쓰지 마라 |
| 2 | **누출** (열린형상 / 반사초과) | 0 또는 매우 작음 | enclosure 가 새고 있다 |
| 3 | **폐쇄성 `Σ B_ab`** | 1 에 매우 가까움 | 위와 같은 원인 |
| 4 | **절점 집합별 추출 변 개수·총면적** | 의도한 값 | 절점을 빠뜨렸다 (6.1절) |
| 5 | **수렴 상태** | 성공 | 실패면 결과가 해가 아니다 |

진단에는 **난수 씨앗, 최대 반사 횟수, `leak_tol`** 도 기록된다. 결과 파일이 무엇으로
만들어졌는지 그 자체로 말하게 하기 위해서다.

### 10.2 상반성 지표 3종

임계값을 쓰지 않는 지표를 함께 낸다.

| 지표 | 성질 |
|---|---|
| `max_rel` | 가장 엄격. **세그먼트가 많으면 1.0 으로 포화한다** |
| `max_abs` | 규모 정규화. 포화하지 않는다 |
| `l1` | 전역 지표. **광선 수 N 에 대해 `N^(−1/2)` 로 감소해야 한다** |

`l1` 이 `N^(−1/2)` 로 줄지 않으면 통계가 아닌 다른 원인이 있다는 신호다.

### 10.3 상세 출력

`[output] detail = true` 로 켜면 `results.npz` 에 배열 세 개가 추가된다.

| 배열 | 크기 | 내용 |
|---|---|---|
| `gebhart_B` | 세그먼트² | Gebhart 흡수계수 행렬 전체 — **크기에 주의** |
| `segment_net_flux` | 세그먼트 | 세그먼트별 순복사 열유속 [W/m²], 안쪽이 양 |
| `nodal_residual` | 절점 | 수렴해에서의 잔차. Dirichlet 절점에서만 0 이 아니며 그 값이 반력이다 |

그 밖의 것은 추가되지 않는다. 요소별 열유속 벡터와 반복별 중간 온도장은
**구현되어 있지 않다.**

---

## 11. 중단 메시지와 대처

| 메시지 | 원인 | 대처 |
|---|---|---|
| `G1 위반 — 야코비안이 양수가 아닌 요소` | 코너 순서가 뒤집혔거나 요소가 퇴화 | 진단의 요소 번호·좌표를 보고 격자를 고쳐라 |
| `G2 위반 — 코너 서명 면적이 양수가 아님` | 코너 순서 오류 | 4.3절의 반시계 규약 확인 |
| `G4 위반 — 부피 상대차` | 연결 배열 오류, 요소 겹침·빈틈, 절점 중복 | 진단의 `duplicate_nodes` 를 먼저 보라 |
| `§10.4 법선 교차검증 실패` | 요소가 심하게 왜곡되었거나 오목 | 진단의 `normal_mismatch` 목록 확인. **끄는 방법은 없다** |
| `§10.7 누출 검사 실패` | enclosure 가 닫혀 있지 않음 / 방사율이 매우 낮음 | 열린형상 누출이면 격자, 반사초과면 `n_bounce_max` |
| `§8.5 위반 — 환경 복사가 자동 복사면과 겹침` | 6.3절 | 그 절점 집합에서 환경 복사를 빼라 |
| `재료 ... 의 열전도도가 0 이하` | 물성 계수 또는 외삽 문제 | `T_range` 와 계수 확인 |
| `격자 지문 불일치` | 격자와 문제 파일의 짝이 어긋남 | 지문을 다시 계산해 넣어라 |
| `최대 반복 ... 에서 수렴하지 않았다` | 허용오차가 통계 잡음보다 작거나 물리적으로 어려움 | 광선 수를 늘리거나 `eps_E` 를 현실적으로 |

**모든 중단은 진단 파일을 끝까지 생성한다.** "중단됐는데 어디가 문제인지 모른다"는
상황이 없도록 설계했다.

---

## 12. 자주 하는 실수

1. **2차 요소의 중간절점을 절점 집합에 넣지 않았다** → 그 변에 경계조건이 걸리지
   않는다. 진단의 추출 변 개수를 보라.
2. **투명 재료에 `k = 0` 을 주었다** → 행렬이 특이해진다. 작은 값을 주어라.
3. **격자를 바꾸고 `mesh_hash` 를 갱신하지 않았다** → 중단된다(의도된 동작).
4. **광선 수를 한 번만 써 보고 결과를 믿었다** → 2배·4배로 늘려 확인하라.
5. **`length_unit` 을 잊었다** → mm 격자를 m 로 읽으면 부피가 10⁹ 배 틀린다.
   진단의 총 부피를 보라.
6. **회색벽 2면 집중식으로 검증하려 했다** → 그 식은 각 면의 복사도가 균일하다고
   가정한다. 일반 형상에서는 성립하지 않는다.
   `docs/BENCHMARK_RESULTS.md` 참조.
7. **대칭축에 단열 조건을 걸었다** → 불필요하다. 무해하지만 의미가 없다.
