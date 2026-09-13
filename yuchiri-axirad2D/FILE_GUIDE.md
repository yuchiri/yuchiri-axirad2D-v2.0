# FILE GUIDE / 파일 안내 — yuchiri-axirad2D v1.1.0

A one-line description of every file. The full illustrated version, covering this
repository and the benchmark suite together, is distributed as
`파일_및_도면_설명서_Files_and_Figures.docx`.

모든 파일의 한 줄 설명. 이 저장소와 벤치마크 모음을 함께 다룬 도면 포함 완전판은
`파일_및_도면_설명서_Files_and_Figures.docx` 로 배포한다.

## Legal / 법적 문서

| File | EN | KO |
|---|---|---|
| `LICENSE` | MIT, plus a note that the name implies no connection with MIT the institution | MIT 원문과 명칭이 기관과 무관하다는 주의 |
| `COPYRIGHT.md` | Copyright holder and free-release declaration | 저작권자 및 무료 공개 선언 |
| `DISCLAIMER.md` | No-warranty notice, applies independently of the licence | 무보증 고지. 라이선스와 별개로 적용 |
| `CITATION.cff` | Citation metadata | 인용 정보 |

## Documentation / 설명서

| File | EN | KO |
|---|---|---|
| `README.md` | Front page: capabilities, design principles, reproducibility, benchmarks | 대문 — 기능, 설계 원칙, 재현성, 벤치마크 |
| `docs/USER_GUIDE.md` | 12-chapter manual; §4.3 node ordering, §11 abort messages | 12장 사용설명서. 4.3절 절점 순서, 11장 중단 메시지 |
| `docs/BENCHMARK_PROBLEMS.md` | BM-1/2/5 definitions, exact answers, sources | BM-1·2·5 정의, 정답, 출처 |
| `docs/BENCHMARK_RESULTS.md` | 15-item comparison, convergence studies, the lumped-formula warning | 15항목 대조, 수렴 연구, 집중식 경고 |
| `docs/benchmark_comparison.csv` | Machine-readable comparison table | 기계 판독용 비교표 |
| `CONTRIBUTING.md` | The seven principles that must not be broken | 깨면 안 되는 원칙 7가지 |
| `CHANGELOG.md` | v1.0.0 and v1.1.0, including the Jacobian defect record | v1.0.0·v1.1.0, 야코비안 결함 기록 포함 |

## Source / 소스

| File | EN | KO |
|---|---|---|
| `src/axirad2d/elements.py` | Shape functions and quadrature, five element types | 형상함수와 적분, 요소 5종 |
| `src/axirad2d/mesh.py` | Mesh, topology, checks G1/G2/G4, fingerprint | 격자, 위상, 검증 G1·G2·G4, 지문 |
| `src/axirad2d/materials.py` | Temperature polynomials; perfusion and metabolic heat (v1.1) | 온도 다항식, 관류·대사 (v1.1) |
| `src/axirad2d/surfaces.py` | Radiating-surface extraction, normal cross-check | 복사면 추출, 법선 교차검증 |
| `src/axirad2d/montecarlo.py` | Ray tracing, Gebhart factors, leakage and reciprocity | 광선 추적, Gebhart 계수, 누출·상반성 |
| `src/axirad2d/assemble.py` | Boundary conditions, residual and Jacobian, perfusion term | 경계조건, 잔차·야코비안, 관류 항 |
| `src/axirad2d/solve.py` | Newton, driver, MPI combination | Newton, 드라이버, MPI 결합 |
| `src/axirad2d/problemio.py` | TOML input, results and diagnostics output | TOML 입력, 결과·진단 출력 |
| `src/axirad2d/cli.py` | Command line; only rank 0 writes | 명령행. 랭크 0 만 기록 |
| `tests/test_axirad2d.py` | All 63 verification tests, including the P3 shape-bias checks added in v1.1 | 검증 시험 63건. v1.1 에서 추가한 P3 형상 편차 검사 포함 |

## Examples and figures / 예제와 도면

| Path | EN | KO |
|---|---|---|
| `examples/gridgen.py` | Mesh generator — NOT part of the solver | 격자 생성기 — 솔버의 일부가 아님 |
| `examples/coaxial_enclosure/` | BM-1 input, reference solution, computed output | BM-1 입력·참조해·계산 결과 |
| `examples/bm2_bm5/` | BM-2 and BM-5 | BM-2·BM-5 |
| `examples/db3/` | DB-3 bioheat example (v1.1); the benchmark itself is in the suite | DB-3 생체열 예제. 벤치마크 본체는 모음에 |
| `figures/benchmark_definitions.png` | The three radiation benchmark geometries | 복사 벤치마크 3종 형상 |
| `figures/results_temperature_fields.png` | Computed fields with the extracted radiating segments | 계산 온도장과 추출된 복사 세그먼트 |
| `figures/results_verification_summary.png` | Six panels of verification evidence | 검증 근거 6패널 |

## Build and CI / 빌드와 CI

| File | EN | KO |
|---|---|---|
| `pyproject.toml` | Package metadata, v1.1.0 | 패키지 메타데이터 |
| `tools/check_reproducibility.py` | Recomputes every shipped output and compares bit for bit; names the two wall-clock fields it ignores | 배포된 출력을 전부 다시 계산해 비트 단위로 비교. 제외하는 벽시계 항목 두 개를 이름으로 밝힌다 |
| `run_all.sh` | Meshes, 63 tests, benchmark, comparison in one command | 한 줄로 격자·시험·벤치마크·대조 |
| `.zenodo.json` | Zenodo DOI metadata | Zenodo DOI 메타데이터 |
| `.github/workflows/tests.yml` | CI: 63 tests plus bit-for-bit MPI reproducibility | CI — 시험 63건과 비트 단위 MPI 재현성 |
| `.github/FUNDING.yml` | **Deliberately empty** — no funding channel is to be opened | **의도적 공백** — 금전 수령 경로를 열지 않는다 |
