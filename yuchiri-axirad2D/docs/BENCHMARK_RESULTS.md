# Benchmark Results / 벤치마크 비교 결과

`yuchiri-axirad2D` v0.1.0 · specification v1.1

**Summary — all 15 compared quantities lie within `|error| < 0.06 %` of exact;
8 of them match exactly.**

Raw data: `benchmark_comparison.csv`
Figures: `../figures/results_temperature_fields.png` (temperature fields),
`../figures/results_verification_summary.png` (verification summary)

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## 0. Principle of these benchmarks

**Every reference value is computed directly from a published expression.
No numerical table from any publication is reproduced.**

The exact solutions rest on **geometric facts, not approximations.**

| Benchmark | Why the exact solution holds |
|---|---|
| BM-1 | The inner body is **convex** and **fully enclosed** → `F(1→2) = 1` follows from geometry alone |
| BM-2 | **Closed-form** view factor for coaxial parallel disks |
| BM-5 | Spherical symmetry makes irradiation on the outer sphere **uniform** → the two-surface lumped formula becomes exact |

## 1. Problem specifications

| | BM-1 coaxial cavity | BM-2 finite cylinder cavity | BM-5 concentric spheres |
|---|---|---|---|
| Geometry | convex inner cylinder in a closed cavity | disk–side wall–disk | concentric spherical shells |
| Nodes / elements | 1025 / 240 | 435 / 98 | 833 / 192 |
| Radiating segments | 56 | 20 | 48 |
| Rays | 40,000 | 60,000 | 40,000 |
| Emissivity | ε₁ = 0.8, ε₂ = 1.0 | all 1.0 (black) | ε₁ = 0.8, ε₂ = 0.5 |
| Heat input | 200 W | 150 W | 300 W |
| Outer boundary | Dirichlet 300 K | Dirichlet 300 K | Dirichlet 300 K |
| Surfaces | planar / straight | planar / straight | **curved (frustum approximation)** |
| View factors | trivial (0, 1) | **non-trivial (0.1716)** | trivial (0, 1) |

## 2. Comparison with exact solutions

| Benchmark | Quantity | Computed | Exact | Unit | Error |
|---|---|---|---|---|---|
| BM-1 | T₁, inner body surface | 564.6711 | 564.6606 | K | **+0.0019 %** |
| BM-1 | Q, net radiative exchange | 200.0162 | 200.0000 | W | **+0.0081 %** |
| BM-1 | F(1→1) | 0.0 | 0 | — | **exact** |
| BM-1 | F(1→2) | 1.000000000000 | 1 | — | **exact** |
| BM-1 | A₁, sum of segments | 0.0471238898 | 0.0471238898 | m² | **diff 6.9e-18** |
| BM-2 | F(disk1→disk2) | 0.171501917 | 0.171572875 | — | **−0.0414 %** |
| BM-2 | F(side→disk1) | 0.207167083 | 0.207106781 | — | **+0.0291 %** |
| BM-2 | F(disk1→disk1) | 0.0 | 0 | — | **exact** |
| BM-2 | A_disk | 0.007853981634 | 0.007853981634 | m² | **exact** |
| BM-2 | A_side | 0.031415926536 | 0.031415926536 | m² | **exact** |
| BM-5 | A₁ (nθ = 48) | 0.020095428 | 0.020106193 | m² | −0.0535 % (discretisation) |
| BM-5 | F(1→1), black | 0.0 | 0 | — | **exact** |
| BM-5 | F(1→2), black | 1.000000000000 | 1 | — | **exact** |
| BM-5 | Q, gray isothermal | 752.0272 | 752.2936 | W | **−0.0354 %** |
| BM-5 | Q, coupled solve | 300.0959 | 300.0000 | W | **+0.0320 %** |

The two BM-2 view factors are **means over 8 seeds**, with standard errors of
0.2636 % and 0.1828 %. The deviations are therefore **0.16 σ** — no evidence of
systematic bias.

The BM-5 `A₁ −0.0535 %` is **not an error but the discretisation** of a sphere by
conical frusta. The `Q` comparison therefore uses the code's own computed areas in
the exact expression, which separates geometric discretisation from radiation
algorithm error.

## 3. Structural checks — must hold exactly

| Item | BM-1 | BM-2 | BM-5 | Requirement |
|---|---|---|---|---|
| G4 divergence-theorem rel. diff. | 1.92e-16 | 4.02e-16 | 4.17e-16 | < tolerance |
| G4 tolerance | 3.41e-12 | 1.39e-12 | 2.73e-12 | `64·n_elem·ε` |
| Normal cross-check mismatches | **0** | **0** | **0** | 0 |
| Leakage (open geometry) | **0.0** | **0.0** | **0.0** | < `leak_tol` |
| Leakage (bounce limit) | **0.0** | **0.0** | **0.0** | < `leak_tol` |
| Closure `Σ B_ab`, minimum | 1.000000000000 | 1.000000000000 | 1.000000000000 | 1 |
| Negative `B` entries | 0 | 0 | 0 | 0 |
| Duplicate nodes | 0 | 0 | 0 | 0 |

## 4. Energy balance

| | Heat input [W] | Dirichlet reaction [W] | Radiation net [W] | Relative residual |
|---|---|---|---|---|
| BM-1 | 200.000000 | −200.000000 | −8.88e-15 | **1.11e-12** |
| BM-2 | 150.000000 | −150.000000 | +3.89e-16 | **5.31e-15** |
| BM-5 | 299.999725 | −299.999725 | −2.84e-14 | **5.68e-14** |

**The radiation net being zero matters.** It means no energy is created or
destroyed inside the enclosure, which holds because closure is exactly 1.

BM-5's input is 299.999725 rather than 300.000 because the faceted mesh has a
**slightly smaller volume** than the true spherical shell, while `q_vol` was
computed from the true volume. Mesh refinement reduces it.

## 5. Convergence

### 5.1 Newton — quadratic

| Iteration | BM-1 `\|ΔT\|/span` | BM-2 | BM-5 |
|---|---|---|---|
| 1 | 2.19e-01 | 1.19e-01 | 2.45e-01 |
| 2 | 6.87e-02 | 2.98e-03 | 1.38e-01 |
| 3 | 4.01e-03 | 1.24e-09 | 2.77e-02 |
| 4 | 1.15e-05 | 1.35e-14 | 7.80e-04 |
| 5 | 9.21e-11 | — | 5.72e-07 |
| 6 | 9.83e-16 | — | 2.05e-11 |
| … | — | — | 3.07e-13 (9 iterations) |

The number of correct digits roughly squares each step — strong evidence that the
fully coupled Newton Jacobian is correct.

This is possible only because **Gebhart factors are computed once per run.**
Re-sampling them every iteration injects fresh statistical noise into the residual
and quadratic convergence cannot be observed.

### 5.2 Monte Carlo — `N^(−1/2)`

Reciprocity L1 residual (BM-1 geometry):

| Rays N | L1 | Ratio | Predicted |
|---|---|---|---|
| 2,500 | 1.3993e-01 | — | — |
| 10,000 | 6.7856e-02 | **0.485** | 0.500 |
| 40,000 | 3.4655e-02 | **0.511** | 0.500 |

### 5.3 Curved surfaces — `Δθ²` (BM-5)

| nθ | Segments | A₁ error | Ratio | Predicted |
|---|---|---|---|---|
| 12 | 24 | −0.8555 % | — | — |
| 24 | 48 | −0.2141 % | **4.00** | 4 |
| 48 | 96 | −0.0535 % | **4.00** | 4 |

Matches the theoretical order for a chord approximating an arc.

## 6. Reproducibility — bit-for-bit

```
reference: serial   435 nodes (BM-2)
  mpi n=1 : bitwise equal = True   max diff 0.000e+00
  mpi n=2 : bitwise equal = True   max diff 0.000e+00
  mpi n=4 : bitwise equal = True   max diff 0.000e+00
```

Gebhart factors computed over disjoint segment subsets and summed are also
**bitwise identical** to the single-pass computation
(`test_V8_batch_invariance_bitwise`).

## 7. ★ Do not use the lumped two-surface gray formula as a verification target

The widely used expression:

```
Q = σ(T₁⁴−T₂⁴) / [ (1−ε₁)/(ε₁A₁) + 1/(A₁F₁₂) + (1−ε₂)/(ε₂A₂) ]
```

**additionally assumes uniform radiosity on each surface.**

### 7.1 Measurements

| Geometry | ε₂ | Difference from this code | On increasing rays |
|---|---|---|---|
| BM-1 cylindrical cavity | 0.6 | **−1.58 %** | **does not shrink** (10,000 → 80,000) |
| BM-1 cylindrical cavity | 1.0 | +0.005 % | — |
| BM-5 concentric spheres | 0.5 | **−0.035 %** | — |

### 7.2 Interpretation

A cylindrical cavity wall is irradiated non-uniformly: the top disk sees a large
part of the inner body, the lower side wall sees it differently. Radiosity is
therefore not uniform.

Concentric spheres are rotationally symmetric, so irradiation on the inner face of
the outer sphere **is** uniform, and the same expression becomes exact.

With ε₂ = 1 there is no reflection, so the assumption is not needed even in the
cylindrical cavity, and the difference falls to 0.005 %.

**Conclusion — the −1.58 % in BM-1 comes from the formula's own assumption, not
from a code defect.** A code that discretises the surfaces actually resolves the
non-uniformity, so disagreement is the correct behaviour.

Without knowing this trap, **a correct code can be misjudged as 1.6 % wrong.**
That is one reason this repository is worth publishing.

## 8. Reproduction

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5

python examples/coaxial_enclosure/build_mesh.py
python examples/bm2_bm5/build_meshes.py

python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python -m axirad2d.cli examples/bm2_bm5/case_bm2.toml -o examples/bm2_bm5/out_bm2
python -m axirad2d.cli examples/bm2_bm5/case_bm5.toml -o examples/bm2_bm5/out_bm5

python examples/coaxial_enclosure/reference.py
python examples/bm2_bm5/verify.py
python examples/plot_results.py
python -m pytest tests -q
```

Random seeds are fixed in the `case.toml` files, so **the same numbers are
reproduced.**

## 9. What is not verified

The following lie **outside the scope of these benchmarks**.

* Transient analysis (not implemented)
* Apparent emissivity of an open cavity with an aperture
* Multiple-reflection accuracy in concave geometry
* Participating-media radiation (unsupported)
* Anisotropic properties (unsupported)
* Memory and performance at large mesh sizes
* Real problems containing triangular elements (3/6-node). Their shape functions
  and quadrature are tested, but all benchmark meshes are 9-node quadrilaterals.

---
---

# 한국어

`yuchiri-axirad2D` v0.1.0 · 사양서 v1.1

**요약 — 정확해 대조 15개 항목 전부 `|오차| < 0.06 %`, 그중 8개는 정확 일치.**

원자료: `benchmark_comparison.csv`
도면: `../figures/results_temperature_fields.png`, `../figures/results_verification_summary.png`

---

## 0. 이 벤치마크들의 원칙

`【사실】` **모든 참조값을 공개된 수식으로 직접 계산했다. 어떤 문헌의 수치표도
복제하지 않았다.**

`【사실】` 정확해의 근거가 **근사식이 아니라 기하학적 사실**이다.

| 벤치마크 | 정확해가 성립하는 이유 |
|---|---|
| BM-1 | 내부물체가 **볼록**하고 공동에 **완전히 포위** → `F(1→2) = 1` 이 기하만으로 성립 |
| BM-2 | 동축 평행 원판의 형상계수 **닫힌 형태** |
| BM-5 | 구대칭이라 바깥 구 내면의 **조사량이 균일** → 2면 집중식이 정확해짐 |

---

## 1. 문제 제원

| | BM-1 동축 원통 공동 | BM-2 유한 원통 공동 | BM-5 동심 구 |
|---|---|---|---|
| 형상 | 볼록 내부 원통 + 닫힌 공동 | 원판–측벽–원판 | 동심 구각 |
| 절점 / 요소 | 1025 / 240 | 435 / 98 | 833 / 192 |
| 복사 세그먼트 | 56 | 20 | 48 |
| 광선 수 | 40,000 | 60,000 | 40,000 |
| 방사율 | ε₁ = 0.8, ε₂ = 1.0 | 전 면 1.0 (흑체) | ε₁ = 0.8, ε₂ = 0.5 |
| 발열 | 200 W | 150 W | 300 W |
| 외곽 | Dirichlet 300 K | Dirichlet 300 K | Dirichlet 300 K |
| 면 | 평면·직선 | 평면·직선 | **곡면 (원뿔대 근사)** |
| 형상계수 | 자명 (0, 1) | **비자명 (0.1716)** | 자명 (0, 1) |

---

## 2. 정확해 대조 — 전체

| 벤치마크 | 항목 | 계산값 | 정확해 | 단위 | 오차 |
|---|---|---|---|---|---|
| BM-1 | T₁ 내부물체 표면온도 | 564.6711 | 564.6606 | K | **+0.0019 %** |
| BM-1 | Q 복사 순교환 | 200.0162 | 200.0000 | W | **+0.0081 %** |
| BM-1 | F(1→1) | 0.0 | 0 | — | **정확** |
| BM-1 | F(1→2) | 1.000000000000 | 1 | — | **정확** |
| BM-1 | A₁ 세그먼트 합 | 0.0471238898 | 0.0471238898 | m² | **차 6.9e-18** |
| BM-2 | F(원판1→원판2) | 0.171501917 | 0.171572875 | — | **−0.0414 %** |
| BM-2 | F(측벽→원판1) | 0.207167083 | 0.207106781 | — | **+0.0291 %** |
| BM-2 | F(원판1→원판1) | 0.0 | 0 | — | **정확** |
| BM-2 | A_원판 | 0.007853981634 | 0.007853981634 | m² | **정확** |
| BM-2 | A_측벽 | 0.031415926536 | 0.031415926536 | m² | **정확** |
| BM-5 | A₁ (nθ = 48) | 0.020095428 | 0.020106193 | m² | −0.0535 % (이산화) |
| BM-5 | F(1→1) 흑체 | 0.0 | 0 | — | **정확** |
| BM-5 | F(1→2) 흑체 | 1.000000000000 | 1 | — | **정확** |
| BM-5 | Q 회색 등온 | 752.0272 | 752.2936 | W | **−0.0354 %** |
| BM-5 | Q 결합 해석 | 300.0959 | 300.0000 | W | **+0.0320 %** |

`【사실】` BM-2 의 두 형상계수는 **씨앗 8개 평균**이며, 표준오차는 각각
0.2636 %, 0.1828 % 다. 따라서 오차는 **0.16 σ** — 계통 편차의 증거가 없다.

`【사실】` BM-5 의 `A₁ −0.0535 %` 는 오차가 아니라 **원뿔대가 구면을 근사한
이산화**다. 그래서 `Q` 대조는 코드가 계산한 면적을 정확해 식에 넣어 수행했다.
그러면 형상 이산화 오차와 복사 알고리즘 오차가 분리된다.

---

## 3. 구조적 판정 — 정확히 성립해야 하는 것

| 항목 | BM-1 | BM-2 | BM-5 | 요구 |
|---|---|---|---|---|
| G4 발산정리 상대차 | 1.92e-16 | 4.02e-16 | 4.17e-16 | < 허용(1e-12 대) |
| G4 허용오차 | 3.41e-12 | 1.39e-12 | 2.73e-12 | `64·n_elem·ε` |
| 법선 교차검증 불일치 | **0** | **0** | **0** | 0 |
| 누출 (열린형상) | **0.0** | **0.0** | **0.0** | < `leak_tol` |
| 누출 (반사초과) | **0.0** | **0.0** | **0.0** | < `leak_tol` |
| 폐쇄성 `Σ B_ab` 최소 | 1.000000000000 | 1.000000000000 | 1.000000000000 | 1 |
| 음의 `B` 성분 | 0 | 0 | 0 | 0 |
| 절점 중복 | 0 | 0 | 0 | 0 |

---

## 4. 에너지 수지

| | 발열 [W] | Dirichlet 반력 [W] | 복사 순합 [W] | 상대 잔차 |
|---|---|---|---|---|
| BM-1 | 200.000000 | −200.000000 | −8.88e-15 | **1.11e-12** |
| BM-2 | 150.000000 | −150.000000 | +3.89e-16 | **5.31e-15** |
| BM-5 | 299.999725 | −299.999725 | −2.84e-14 | **5.68e-14** |

`【사실】` **복사 순합이 0 이라는 것이 중요하다.** enclosure 내부에서 에너지가
생성·소멸하지 않음을 뜻하며, 폐쇄성이 정확히 1 이기 때문에 성립한다.

`【사실】` BM-5 의 발열이 300.000 이 아니라 299.999725 인 것은, 구를 원뿔대로
근사한 격자의 **부피가 참 구각보다 약간 작기** 때문이다. `q_vol` 은 참 부피
기준으로 계산했으므로 그 차이가 그대로 나타난다. 격자를 세분하면 줄어든다.

---

## 5. 수렴

### 5.1 Newton — 2차 수렴

| 반복 | BM-1 `\|ΔT\|/범위` | BM-2 | BM-5 |
|---|---|---|---|
| 1 | 2.19e-01 | 1.19e-01 | 2.45e-01 |
| 2 | 6.87e-02 | 2.98e-03 | 1.38e-01 |
| 3 | 4.01e-03 | 1.24e-09 | 2.77e-02 |
| 4 | 1.15e-05 | 1.35e-14 | 7.80e-04 |
| 5 | 9.21e-11 | — | 5.72e-07 |
| 6 | 9.83e-16 | — | 2.05e-11 |
| … | — | — | 3.07e-13 (9회) |

`【사실】` 오차의 자릿수가 대략 제곱으로 줄어든다. 완전 결합 Newton 야코비안이
올바르다는 강한 증거다.

`【사실】` 이것이 가능한 이유는 **Gebhart 계수를 실행당 1회만 계산**하기 때문이다.
반복마다 다시 뽑으면 잔차에 통계 잡음이 계속 들어와 2차 수렴이 관측되지 않는다.

### 5.2 몬테카를로 — 통계 수렴 `N^(−1/2)`

상반성 L1 잔차 (BM-1 형상):

| 광선 수 N | L1 | 감소비 | 예측 |
|---|---|---|---|
| 2,500 | 1.3993e-01 | — | — |
| 10,000 | 6.7856e-02 | **0.485** | 0.500 |
| 40,000 | 3.4655e-02 | **0.511** | 0.500 |

### 5.3 곡면 근사 — `Δθ²` 수렴 (BM-5)

| nθ | 세그먼트 | A₁ 오차 | 감소비 | 예측 |
|---|---|---|---|---|
| 12 | 24 | −0.8555 % | — | — |
| 24 | 48 | −0.2141 % | **4.00** | 4 |
| 48 | 96 | −0.0535 % | **4.00** | 4 |

`【사실】` 현(弦)이 원호를 근사할 때의 이론 차수와 일치한다.

---

## 6. 재현성 — 비트 단위

```
기준: serial   절점 435 (BM-2)
  mpi n=1 : 비트 단위 일치 = True   최대차 0.000e+00
  mpi n=2 : 비트 단위 일치 = True   최대차 0.000e+00
  mpi n=4 : 비트 단위 일치 = True   최대차 0.000e+00
```

`【사실】` 세그먼트를 부분집합으로 나누어 계산한 Gebhart 계수도 통합 계산과
**비트 단위로 일치**한다 (`test_V8_batch_invariance_bitwise`).

---

## 7. ★ 회색벽 2면 집중식을 검증 기준으로 쓰지 말 것

`【사실】` 널리 쓰이는 식:

```
Q = σ(T₁⁴−T₂⁴) / [ (1−ε₁)/(ε₁A₁) + 1/(A₁F₁₂) + (1−ε₂)/(ε₂A₂) ]
```

`【사실】` 이 식은 **각 면의 복사도가 균일**하다고 **추가로** 가정한다.

### 7.1 실측

| 형상 | ε₂ | 집중식과의 차이 | 광선 수를 늘리면 |
|---|---|---|---|
| BM-1 원통 공동 | 0.6 | **−1.58 %** | **줄지 않음** (10,000 → 80,000) |
| BM-1 원통 공동 | 1.0 | +0.005 % | — |
| BM-5 동심 구 | 0.5 | **−0.035 %** | — |

### 7.2 해석

`【사실】` 원통 공동벽은 부위마다 조사량이 다르다. 위쪽 원판은 내부물체를 크게
보고, 측벽 아래쪽은 다르게 본다. 따라서 복사도가 균일하지 않다.

`【사실】` 동심 구는 회전 대칭성 때문에 바깥 구 내면의 조사량이 **균일**하다.
그래서 같은 식이 정확해진다.

`【사실】` ε₂ = 1 로 두면 반사가 없어 원통 공동에서도 가정이 필요 없어지고,
차이가 0.005 % 로 떨어진다.

`【결론】` **BM-1 의 −1.58 % 는 코드 결함이 아니라 집중식 자체의 가정 때문이다.**
면을 세분해 푸는 코드가 그 비균일성을 실제로 계산하므로 다른 것이 정상이다.

`【해석】` 이 함정을 모르면 **정상 코드를 1.6 % 틀렸다고 오판**할 수 있다.
본 저장소가 공개할 가치가 있다고 보는 이유 중 하나다.

---

## 8. 재현 방법

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5

# 격자 생성
python examples/coaxial_enclosure/build_mesh.py
python examples/bm2_bm5/build_meshes.py

# 계산
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python -m axirad2d.cli examples/bm2_bm5/case_bm2.toml -o examples/bm2_bm5/out_bm2
python -m axirad2d.cli examples/bm2_bm5/case_bm5.toml -o examples/bm2_bm5/out_bm5

# 정확해 대조
python examples/coaxial_enclosure/reference.py
python examples/bm2_bm5/verify.py

# 도면
python examples/plot_results.py

# 시험 63건
python -m pytest tests -q
```

`【사실】` 난수 씨앗이 `case.toml` 에 고정되어 있으므로 **같은 숫자가 재현된다.**

---

## 9. 검증되지 않은 것

`【사실】` 아래는 **본 벤치마크의 범위 밖이다.**

* 과도 해석 (미구현)
* 개구가 있는 열린 공동의 겉보기 방사율
* 오목 형상에서의 다중 반사 정밀도
* 참여 매질 복사 (미지원)
* 이방성 물성 (미지원)
* 대규모 격자에서의 메모리·성능
* 삼각형 요소(3·6절점)를 포함한 실제 문제 — 형상함수와 적분은 시험되었으나
  벤치마크 격자는 전부 9절점 사각형이다
