# COPYRIGHT — Copyright holder and free-release declaration
# 저작권자 및 무료 공개 선언

**Project / 프로젝트** yuchiri-axibio-bench
**Version / 버전** 0.2.0
**Copyright holder / 저작권자** **Yoo Cheol WON (원유철)**
**Year / 연도** 2026
**License / 라이선스** MIT (see `LICENSE`)

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## 1. Declaration

I, **Yoo Cheol WON**, am the copyright holder of yuchiri-axibio-bench.

I release this software to the public **free of charge and without
consideration of any kind**, under the MIT License.

Concretely, this means:

* **No fee.** Not now, and not for any future version.
* **No consideration.** No donation channel, no sponsorship, no paid support,
  no paid consulting, no dual licensing.
* **No restriction on use.** Commercial use, modification, redistribution and
  sublicensing are all permitted.
* **One condition only.** Retain the copyright notice and the permission
  notice, as stated in `LICENSE`. This exists so that the origin of the work
  remains traceable, not to extract anything from the user.

This repository deliberately contains an empty `.github/FUNDING.yml` so that no
funding channel is opened by accident.

## 1a. A note on the name "MIT License"

**"MIT License" is the historical name of a standard permissive licence form.
It implies no connection with, and no endorsement by, the Massachusetts
Institute of Technology.**

Using this licence creates no affiliation, no sponsorship, no approval and no
obligation towards that institution. No permission from anyone is required to
use it. The same is true of the other licences named after their origin —
Apache, BSD, ISC.

**The copyright holder of this software is Yoo Cheol WON.** The MIT License is
simply the wording by which that copyright holder grants permission to others.

Separately: the mathematics and algorithms this software implements — Galerkin
finite elements, Gauss quadrature, Gebhart absorption factors, closed-form view
factors — are **not subject to copyright at all**, so consulting the published
literature about them required no licence and creates no obligation. What is
licensed here is the author's own expression, i.e. the code.

## 2. What is and is not covered

| Covered by this declaration | Not covered |
|---|---|
| Source code in `benchmarks/` | Third-party dependencies (NumPy, SciPy, mpi4py — each under its own BSD-family licence) |
| Tests, examples, mesh and input files, computed output files | Mathematical results and physical laws, which are not subject to copyright in the first place |
| Documentation, figures | — |

## 3. Provenance statement

This software contains **no geometry coordinates of any device, no material
coefficients for any specific substance, and no boundary conditions of any
specific problem.** Geometry, mesh, materials, heat sources and boundary
conditions are all supplied by the user as input.

The algorithms are public knowledge: Galerkin finite elements, isoparametric
elements, Gauss quadrature, Gebhart absorption factors, Monte Carlo ray tracing,
Newton–Raphson, backward Euler.

Benchmark reference values are computed directly from published expressions.
**No numerical table from any publication is reproduced.**

## 4. AI use disclosure

This software was written **using Anthropic's Claude as a tool.** The design
decisions — more than twenty of them, covering mesh input strategy, element
types, radiating-surface extraction, normal determination, boundary conditions,
coupling scheme, convergence criterion, parallel strategy and output policy —
were made by the human author, and those decisions determine the structure of
the code. Claude was used to turn them into code and tests.

See the "AI use disclosure" section of `README.md`.

## 5. No warranty

This declaration grants rights. It grants **no warranty of any kind.**
See `DISCLAIMER.md`, which is written to apply independently of this
declaration and of the licence.

**Do not use this software as design evidence for safety-related systems.**

## 6. Contact

Issues and pull requests via the repository. The author promises no maintenance,
no support and no response time.

---
---

# 한국어

## 1. 선언

본인 **원유철(Yoo Cheol WON)** 은 yuchiri-axibio-bench 의 저작권자이다.

본인은 이 소프트웨어를 **어떠한 대가도 없이 무상으로** MIT 라이선스에 따라
공중에 공개한다.

구체적으로 다음을 뜻한다.

* **대금을 받지 않는다.** 현재도, 장래의 어떤 버전에 대해서도 받지 않는다.
* **어떠한 대가도 받지 않는다.** 후원 창구, 스폰서십, 유료 지원, 유료 자문,
  이중 라이선스를 두지 않는다.
* **사용에 제한을 두지 않는다.** 상업적 이용, 개작, 재배포, 재실시권 부여를
  모두 허용한다.
* **조건은 하나뿐이다.** `LICENSE` 에 적힌 대로 저작권 표시와 허가 표시를
  유지하는 것. 이는 저작물의 출처가 추적 가능하게 남기기 위한 것이지,
  사용자로부터 무엇을 얻기 위한 것이 아니다.

이 저장소는 금전 수령 창구가 실수로 열리지 않도록 `.github/FUNDING.yml` 을
**의도적으로 비워 두었다.**

## 1a. "MIT 라이선스" 라는 명칭에 관하여

**"MIT 라이선스" 는 표준 허가형 라이선스 양식의 관용적 명칭이다. 매사추세츠
공과대학교와 어떠한 관련도 없으며, 그 기관의 승인을 뜻하지도 않는다.**

이 라이선스를 사용한다고 해서 그 기관과의 제휴·후원·승인 관계가 생기지 않으며,
그 기관에 대한 어떤 의무도 발생하지 않는다. 사용에 누구의 허락도 필요 없다.
유래에서 이름을 딴 다른 라이선스들 — Apache, BSD, ISC — 도 마찬가지다.

**본 소프트웨어의 저작권자는 원유철(Yoo Cheol WON)이다.** MIT 라이선스는 그
저작권자가 타인에게 허락을 부여하는 **문안**일 뿐이다.

한편 이 소프트웨어가 구현한 수학과 알고리즘 — Galerkin 유한요소법, Gauss 구적,
Gebhart 흡수계수, 닫힌 형태 형상계수 — 은 **애초에 저작권의 대상이 아니다.**
따라서 공개된 문헌을 참고하는 데 어떤 라이선스도 필요하지 않았고, 그로 인해
발생하는 의무도 없다. 여기서 라이선스되는 것은 **저작자 자신의 표현물, 즉 코드**다.

## 2. 이 선언이 미치는 범위

| 미치는 것 | 미치지 않는 것 |
|---|---|
| `benchmarks/` 의 소스 코드 | 제3자 의존성 (NumPy, SciPy, mpi4py — 각각 BSD 계열 자체 라이선스) |
| 시험, 예제, 격자·입력 파일, 계산 결과 파일 | 수학적 결과와 물리 법칙. 애초에 저작권 대상이 아니다 |
| 문서, 도면 | — |

## 3. 계보 선언

이 소프트웨어에는 **어떤 장치의 형상 좌표도, 특정 재료의 물성 계수도, 특정
문제의 경계조건도 들어 있지 않다.** 형상·격자·물성·열원·경계조건은 전부
사용자가 입력으로 제공한다.

알고리즘은 전부 공지 기술이다 — Galerkin 유한요소법, 등매개 요소, Gauss 구적,
Gebhart 흡수계수, 몬테카를로 광선 추적, Newton–Raphson, 후진 오일러.

벤치마크 참조값은 공개된 수식으로 직접 계산했다.
**어떤 문헌의 수치표도 복제하지 않았다.**

## 4. AI 사용 고지

이 소프트웨어는 **Anthropic 의 Claude 를 도구로 사용하여 작성되었다.** 격자 입력
방식, 요소 종류, 복사면 추출, 법선 판정, 경계조건, 연성 방식, 수렴 판정, 병렬
방식, 출력 정책 등 **20여 개의 설계 결정을 사람이 내렸고, 그 결정이 코드의 구조를
규정한다.** Claude 는 그 결정을 코드와 시험으로 옮기는 데 사용되었다.

`README.md` 의 "AI 사용 고지" 절을 참조하라.

## 5. 무보증

이 선언은 권리를 부여한다. **어떠한 보증도 부여하지 않는다.**
`DISCLAIMER.md` 를 보라. 그 문서는 이 선언 및 라이선스와 **별개로** 적용되도록
작성되었다.

**안전 관련 시스템의 설계 근거로 사용하지 말 것.**

## 6. 연락

문제 제기와 기여는 저장소를 통해 받는다. 저작자는 유지보수, 기술 지원, 회신 시한을
약속하지 않는다.
