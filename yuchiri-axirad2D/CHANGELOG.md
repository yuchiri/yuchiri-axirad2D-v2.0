# Changelog / 변경 이력

Format follows [Keep a Changelog](https://keepachangelog.com/).

---

# English

## [2.0.0] — 2026-09

### Breaking

* `solve_steady` now takes a `blood` keyword and returns **five** values instead
  of four: the fifth is a dict of detailed output arrays. Callers that unpacked
  four values must be updated. This is why the version is 2.0 rather than 1.2.

### Added

* `tools/check_reproducibility.py` — recomputes every shipped mesh and output and
  compares them bit for bit with the committed ones. Two wall-clock timing fields
  in `diagnostics.json` cannot be reproducible; the tool names them rather than
  quietly excluding them. Verified on a clean extract of the release archive:
  everything else, **including the figure PNGs**, is byte-identical.

### Fixed — found by running the shipped archive as a new user would

* **The README promised Python 3.9; the code required 3.11.** The problem file is
  TOML, and `tomllib` only entered the standard library in 3.11. macOS ships 3.9
  with the Xcode command line tools, so a Mac user following the README would have
  hit `ModuleNotFoundError: tomllib`. The reader now falls back to `tomli` on 3.9
  and 3.10, fails with an instruction rather than a bare import error if neither is
  present, and the README states the requirement accurately.
* **A test that guards against drift between two copies of the property file was
  skipping forever**, because it looked for the suite under a directory name the
  published archive does not use. It now finds it, and runs.

### Fixed — found by a third review before release

* **A problem with no temperature reference reported "did not converge".** With
  no Dirichlet, convection or environment-radiation condition the steady matrix is
  singular; Newton merely diverged and the message pointed at the wrong thing. The
  absence is now detected up front and named.
* The benchmark suite's report checker **passed a report containing no cases at
  all**, and did not notice cases the reference requires but the report omits.
  Both now fail. Silence is not agreement.

### Fixed — found by a second review before release

* **A problem driven only by Dirichlet conditions was reported as not converged**,
  even when the solution was exact to 1e-16. The energy imbalance was normalised
  by the *net* power input, which is zero for such a problem, so the criterion
  divided by zero. It is now normalised by the heat **throughput** — the absolute
  sum of the Dirichlet reactions — which is non-zero whenever heat actually flows.
  The benchmark numbers are unchanged, because their net input is large. A
  regression test covers it.
* Input errors — a wrong mesh fingerprint, a missing file, a malformed problem
  file — now end with a single clear line and exit code 2, instead of a Python
  traceback.
* Diagnostics record the parallel mode even when a problem has no radiating
  surfaces, and the radiation parameter line is omitted rather than printed with
  nulls.

### Added

* **Pennes perfusion term** `omega_b rho_b c_b (T_a - T)` and **metabolic heat
  generation**, as volumetric contributions. Blood properties (`rho_cb`,
  `T_arterial`) live at problem level, not per material, because they are
  properties of blood and duplicating them per tissue would let them disagree.
  Requesting perfusion without blood properties **aborts** rather than silently
  treating the sink as zero.
* **DB-3 benchmark** — layered skin with perfusion and radiative surface loss,
  compared against an exact solution derived from a layer transfer matrix plus a
  single scalar Newton solve. Nodal L-infinity error 7.4e-09 K on the finest
  mesh; observed order of convergence 3.90.
* Ten further verification tests (53 -> 63).

### Fixed

* **The P3 shape-bias diagnostic was documented but not implemented.** The
  README, the user guide and the disclaimer all stated that the deviation between
  the curved element edge seen by conduction and the straight frustum seen by
  radiation is always reported; the code wrote a null placeholder instead. It is
  now computed, from an independent quadrature of the curved edge, and reported
  in full. On straight-edged meshes it is ~1e-16; on the polar mesh of BM-5 it is
  **2.14e-03**, which reproduces the independently measured faceting error of
  0.214 % — a cross-check the diagnostic passes on its first use.
* References to an unpublished internal specification were removed from the
  published source and replaced with references to the user guide, so that every
  pointer in the code can actually be followed by a reader.
* **A claim audit was run over every public document**, checking each stated
  behaviour against the code. Two further gaps were found and closed: the random
  seed, maximum bounce count and leakage tolerance were not recorded in the
  diagnostics, so a result file could not state what produced it; and the
  detailed-output switch wrote only the Gebhart matrix. Per-segment net radiative
  flux and the nodal residual are now written as well, and the user guide states
  plainly that element-wise flux vectors and per-iteration fields are **not**
  implemented. Two tests now assert that every documented output actually appears.
* Unused imports and variables removed; the public tree is clean under pyflakes.
* Two superseded example files removed, and the figure filenames made ASCII.

### Guaranteed

* With `perfusion = 0` the results are **bit-for-bit identical** to v1.0.0.
  Verified on BM-1 and BM-5.

## [1.0.0] — 2026-08

First public release.

### Added

* **Five element types** — 3/6-node triangles, 4/8/9-node quadrilaterals,
  mixable within a single mesh
* **Mesh entirely as external input** — the code does not generate meshes
* **Mesh checks** G1 (Jacobian), G2 (area cross-check), G4 (divergence theorem).
  Abort without auto-correction
* **Automatic radiating-surface extraction** from transparent/opaque material
  tags; enclosure count never hard-coded
* **Normal cross-check** — topological determination plus geometric verification;
  mismatch aborts after writing diagnostics
* **Monte Carlo Gebhart factors** — batch-invariant, leakage counted by cause,
  abort above `leak_tol`. Closure is never renormalised and reciprocity never
  symmetrised
* **Fully coupled Newton** with the complete radiation Jacobian; quadratic
  convergence observed
* **AND convergence condition** — both temperature increment and energy imbalance
* **Five boundary condition types** — Dirichlet, heat flux, adiabatic/symmetry,
  convection, environment radiation
* **MPI parallel with bit-for-bit reproducibility** — serial = mpi(1) = mpi(2) =
  mpi(4), measured
* **Standard diagnostics always written** — mesh checks, radiation diagnostics,
  energy balance, node-set face extraction
* **Three benchmarks** — coaxial cylindrical cavity, finite cylinder cavity,
  concentric spheres
* **53 verification tests**

### Not implemented

* Transient analysis (backward Euler); it is fixed in the specification
* Schur static condensation (interface only)
* Some detailed outputs

### Fixed before release

* **Transposed Jacobian inverse in `mesh.py:elem_geom`.** The components `J12`
  and `J21` were interchanged when inverting the isoparametric Jacobian. On
  axis-aligned meshes `J12 = J21 = 0`, so the error cancelled exactly and was
  invisible; it only appeared on non-axis-aligned elements. Found by a
  refinement study in which 6-node triangles failed to converge — the error
  stagnated at 154 K (ratio 1.05) while 9-node quadrilaterals converged
  normally. After the fix the triangles converge at ratio 7.3, close to the
  theoretical order for quadratic elements.

  Three regression tests were added: gradients on a **non-axis-aligned**
  element for all five types, a **patch test** (zero interior residual for a
  linear field), and a **mesh convergence** check against the `ln r` solution.
  Re-injecting the defect makes 9 of them fail.

  Effect on the benchmarks: BM-1 and BM-2 use orthogonal meshes and were
  unchanged. BM-5 uses a polar mesh and changed slightly — peak temperature
  797.94 → 797.65 K, Q 300.0929 → 300.0959 W.

### Known limitations

See `DISCLAIMER.md` §4.

---
---

# 한국어


## [0.1.0] — 2026-08

첫 공개.

### 추가

* **요소 5종** — 삼각 3·6절점, 사각 4·8·9절점. 한 격자에 혼합 가능
* **격자 외부 입력** — 코드는 격자를 만들지 않는다
* **격자 검증** G1(야코비안), G2(면적 대조), G4(발산정리). 자동 교정 없이 중단
* **복사면 자동 추출** — 재료의 투명/불투명 표시만으로 면과 enclosure 를 찾는다.
  enclosure 개수를 하드코딩하지 않는다
* **법선 교차검증** — 위상 판정 + 기하 판정. 불일치 시 진단 후 중단
* **몬테카를로 Gebhart 계수** — 배치 불변, 누출 원인별 계수, `leak_tol` 초과 시 중단.
  폐쇄성 자동 보정과 상반성 대칭화를 하지 않는다
* **완전 결합 Newton** — 복사 야코비안 전항 조립. 2차 수렴 관측
* **AND 수렴 조건** — 온도 증분과 에너지 불균형을 둘 다 요구
* **경계조건 5종** — Dirichlet, 열유속, 단열/대칭, 대류, 환경 복사
* **MPI 병렬 + 비트 단위 재현성** — serial = mpi(1) = mpi(2) = mpi(4) 실측 확인
* **표준 진단 상시 출력** — 격자 검증, 복사 진단, 에너지 수지, 절점 집합 추출 결과
* **벤치마크 3종** — 동축 원통 밀폐공동, 유한 원통 밀폐공동, 동심 구
* **검증 시험 53건**

### 미구현

* 과도 해석 (후진 오일러). 사양서에는 확정되어 있다
* Schur 정적 응축 (인터페이스만 존재)
* 상세 출력 일부

### 공개 전 수정

* **`mesh.py:elem_geom` 의 야코비안 역행렬 성분 뒤바뀜.** 등매개 야코비안을
  역산할 때 `J12` 와 `J21` 을 서로 바꿔 썼다. 축에 정렬된 격자에서는
  `J12 = J21 = 0` 이라 오류가 정확히 상쇄되어 드러나지 않았고, 비직교 요소에서만
  나타났다. 6절점 삼각형이 수렴하지 않는 것을 격자 세분으로 발견했다 —
  오차가 154 K 에서 정체했고(감소비 1.05) 9절점 사각형은 정상 수렴했다.
  수정 후 삼각형의 감소비는 7.3 으로, 2차 요소의 이론 차수에 부합한다.

  회귀 시험 3건을 추가했다 — 5종 전부에 대한 **비직교 요소**에서의 기울기,
  **패치 시험**(선형장에서 내부 절점 잔차 0), `ln r` 정확해 대비 **격자 수렴**.
  결함을 되살리면 그중 9건이 실패한다.

  벤치마크에 미친 영향 — BM-1·BM-2 는 직교 격자라 변화 없음. BM-5 는 극좌표
  격자여서 약간 변했다 (최고온도 797.94 → 797.65 K, Q 300.0929 → 300.0959 W).

### 알려진 한계

`DISCLAIMER.md` 4절 참조.
