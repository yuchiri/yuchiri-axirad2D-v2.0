# DISCLAIMER — No-warranty notice / 무보증 고지

*English first · 한국어는 아래에 이어집니다*

---
---

# English

**This document is intended to be read independently of the license.**
It is intended to apply regardless of whether copyright subsists and regardless
of the validity of the license.

## 1. No warranty

This software is provided **"AS IS", without warranty of any kind.**
No warranty of merchantability, fitness for a particular purpose, or
non-infringement is given.

The author is **not liable for any damages** arising from the use of, or
inability to use, this software. This includes but is not limited to direct,
indirect, incidental and consequential damages, data loss, equipment damage,
personal injury and business loss.

## 2. What this software does and does not do

This code **computes a temperature field.** Using those numbers for design,
safety, certification, operation or procurement decisions is **entirely the
user's responsibility.**

The author does not:

* warrant that the results match the behaviour of any real device;
* judge whether the user's mesh, properties or boundary conditions are sound;
* promise maintenance, technical support or defect correction;
* promise backward compatibility.

## 3. Scope of verification — understand this

"Verified" means the results agreed with exact solutions **within the scope of
the three benchmarks included in this repository.** Nothing is warranted outside
that scope.

| Verified | Not verified |
|---|---|
| Axisymmetric conduction (`ln r` analytic solution) | Participating-media radiation (unsupported) |
| Surface-to-surface radiation, view factors | Transient analysis (**not implemented**) |
| Convex body fully enclosed; coaxial parallel disks; concentric spheres | Multiple-reflection accuracy in concave geometry |
| Curved surfaces via frustum approximation (Δθ² convergence) | Open cavities with an aperture |
| **Triangular and mixed meshes** — patch test and `ln r` mesh convergence | Large-scale problems using triangles |
| Gray reflection (concentric spheres) | Anisotropic properties (unsupported) |
| serial = MPI bit-for-bit reproducibility | Memory and performance at large mesh sizes |

## 4. Known limitations — where it can be silently wrong

These are **not defects but accepted design consequences.** They are dangerous
if you do not know about them.

1. **Cyclic node rotation, misplaced mid-side nodes and wrong node counts may go
   undetected.** The mid-side position check (G3) was omitted to avoid
   introducing an unjustified threshold. Passing G1/G2/G4 does not exclude these.
2. **Mid-side nodes of quadratic elements receive no radiative flux.** Radiating
   segments are straight frusta defined by two corner nodes.
3. **Conduction and radiation see different geometry** — curved edges vs straight
   approximation.
4. **Monte Carlo statistical error propagates into the solution and does not
   shrink with iteration.** Gebhart factors are computed once per run. Assess it
   yourself by varying the ray count.
5. **Tolerances tighter than the statistical noise always end in convergence
   failure.**
6. **Transparent materials need a small non-zero `k`.** With `k = 0` the
   equations for interior nodes of that region become singular. Temperatures
   plotted in that region have no physical meaning.
7. **MPI reproducibility costs memory proportional to process count.**

## 5. Warning for safety and certification use

This software was **not designed or intended for safety-related calculations,
regulatory certification, or as design evidence for pressure vessels, nuclear
plant, medical devices or similar.** For such purposes use tools with the
verification-and-validation procedures and quality assurance systems required in
that field.

## 6. AI use disclosure

This software was written **using Anthropic's Claude as a tool.** Design
decisions were made by a human; Claude was used to turn them into code and tests.
See the "AI use disclosure" section of `README.md`.

**This fact changes nothing in the no-warranty statement above.**

## 7. Before you trust the results

1. Run `bash run_all.sh` and confirm the 63 tests pass **in your own environment**.
2. Pick the benchmark closest to your problem and check convergence under mesh
   refinement.
3. Double and quadruple the ray count and check the result does not move.
4. **Always check the energy-balance relative residual** in the diagnostics
   output. If it is off, something is wrong.
5. Cross-check against another code or an analytic solution where possible.

---
---

# 한국어

**이 문서는 라이선스와 별개로 읽히도록 의도되었다.**
저작권 보호 여부, 라이선스의 유효성 여부와 관계없이 아래 내용이 적용될 것을 의도한다.

---

## 1. 보증하지 않는다

이 소프트웨어는 **아무런 보증 없이 "있는 그대로(AS IS)"** 제공된다.
상품성, 특정 목적 적합성, 비침해에 대한 어떤 보증도 하지 않는다.

작성자는 이 소프트웨어의 사용 또는 사용 불능으로 발생하는 **어떤 손해에 대해서도
책임지지 않는다.** 여기에는 직접·간접·부수적·결과적 손해, 데이터 손실, 장비 손상,
인적 피해, 영업 손실이 포함되며 이에 한정되지 않는다.

## 2. 이 소프트웨어가 하는 일과 하지 않는 일

이 코드는 **온도 분포를 계산한다.** 그 숫자를 설계·안전·인증·운전·구매 판단에
사용하는 것은 **전적으로 사용자의 책임**이다.

작성자는 다음을 하지 않는다.

* 계산 결과가 실제 장치의 거동과 일치한다는 보증
* 사용자의 격자·물성·경계조건이 타당한지에 대한 판단
* 유지보수, 기술 지원, 결함 수정에 대한 약속
* 하위 호환성 유지에 대한 약속

## 3. 검증의 범위 — 반드시 이해할 것

`검증되었다`는 말은 **본 저장소에 포함된 벤치마크 3종의 범위 안에서** 정확해와
일치했다는 뜻이다. 그 범위를 벗어난 문제에 대해서는 아무것도 보증하지 않는다.

| 검증된 것 | 검증되지 않은 것 |
|---|---|
| 축대칭 전도 (`ln r` 해석해) | 참여 매질 복사 (미지원) |
| 표면 대 표면 복사, 형상계수 | 과도 해석 (**미구현**) |
| 볼록체 완전 포위, 동축 평행 원판, 동심 구 | 오목 형상의 다중 반사 정밀도 |
| 곡면의 원뿔대 근사 (Δθ² 수렴) | 개구가 있는 열린 공동 |
| **삼각형·혼합 격자** — 패치 시험과 `ln r` 격자 수렴 | 삼각형을 쓴 대규모 문제 |
| 회색 반사 (동심 구) | 이방성 물성 (미지원) |
| 직렬 = MPI 비트 단위 재현성 | 대규모 격자에서의 메모리·성능 |

## 4. 알려진 한계 — 조용히 틀릴 수 있는 곳

아래는 **결함이 아니라 설계상 감수한 것**이다. 그러나 모르고 쓰면 위험하다.

1. **절점 순환 이동, 중간절점 오배치, 절점 수 오기는 검출되지 않을 수 있다.**
   근거 없는 임계값을 도입하지 않기 위해 중간절점 위치 판정(G3)을 두지 않았다.
   격자 검증 G1·G2·G4를 통과해도 이 오류는 남을 수 있다.
2. **2차 요소의 중간절점은 복사 열유속을 받지 않는다.**
   복사면은 코너 절점 2개로 정의되는 직선 원뿔대다.
3. **전도와 복사가 서로 다른 형상을 본다.** 전도는 곡선 변, 복사는 직선 근사.
4. **몬테카를로 통계 오차는 해에 그대로 반영되며 반복해도 줄지 않는다.**
   Gebhart 계수는 실행당 1회만 계산한다. 오차 확인은 광선 수를 바꿔 직접 하라.
5. **허용오차를 통계 잡음보다 작게 주면 항상 수렴 실패로 종료된다.**
6. **투명 재료에도 0이 아닌 작은 `k` 를 주어야 한다.** `k = 0` 이면 그 영역
   내부 절점의 방정식이 특이해진다. 그 영역에 그려지는 온도는 물리적 의미가 없다.
7. **MPI 재현성을 위해 메모리를 프로세스 수에 비례해 사용한다.**

## 5. 안전·인증 용도에 대한 경고

이 소프트웨어는 **안전 관련 계산, 규제 인증, 압력용기·원자력·의료기기 등의
설계 근거**로 사용할 것을 의도하고 만들어지지 않았다. 그런 용도에는 해당 분야의
검증·확인(V&V) 절차와 품질보증 체계를 갖춘 도구를 사용하라.

## 6. AI 사용 고지

이 소프트웨어는 **Anthropic 의 Claude 를 도구로 사용하여 작성되었다.**
설계 결정은 사람이 했고, Claude 는 그 결정을 코드와 시험으로 옮기는 데 쓰였다.
자세한 내용은 `README.md` 의 "AI 사용 고지" 절을 보라.

이 사실이 위 무보증 고지의 어떤 부분도 바꾸지 않는다.

## 7. 결과를 신뢰하기 전에 할 일

1. `bash run_all.sh` 를 실행해 **자신의 환경에서** 시험 63건이 통과하는지 확인하라.
2. 자신의 문제와 가장 가까운 벤치마크를 골라, 격자를 세분하며 결과가 수렴하는지 보라.
3. 광선 수를 2배, 4배로 늘려 결과가 변하지 않는지 확인하라.
4. 진단 출력의 **에너지 수지 상대 잔차**를 반드시 확인하라. 이것이 어긋나면
   어딘가 틀린 것이다.
5. 가능하면 다른 코드 또는 해석해와 교차 확인하라.
