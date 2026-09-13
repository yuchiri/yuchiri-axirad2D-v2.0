# FILE GUIDE / 파일 안내 — yuchiri-axibio-bench v0.2.0

A one-line description of every file. The full illustrated version is
`파일_및_도면_설명서_Files_and_Figures.docx`.

모든 파일의 한 줄 설명. 도면 포함 완전판은
`파일_및_도면_설명서_Files_and_Figures.docx`.

## Top level / 최상위

| File | EN | KO |
|---|---|---|
| `README.md` | What the suite is and is not, benchmark list, acceptance rule, results | 모음의 성격, 벤치마크 목록, 합격 규칙, 결과 |
| `SPEC.md` | The specification: scope, governing equation, entry requirements, acceptance by order of convergence, report schema, eight open items | 사양서 — 범위, 지배방정식, 항목 요건, 수렴 차수 합격 기준, 보고 형식, 미결 8건 |
| `requirements.txt` | numpy; matplotlib only for redrawing figures | numpy. matplotlib 은 도면 재생성에만 |
| `DISCLAIMER.md` | **No-warranty notice and statement of intended use: no medical purpose; verification, not validation** | **무보증 고지 및 사용 목적 선언 — 의료 목적 없음, 검증이지 확인이 아님** |
| `LICENSE`, `COPYRIGHT.md` | MIT; copyright holder and free-release declaration | MIT, 저작권자 및 무료 공개 선언 |

## DB-3 — layered skin / 다층 피부

| File | EN | KO |
|---|---|---|
| `problem.md` | Definition, property provenance (every value marked LIT or SCENARIO), derivation, four self-consistency checks, and what it does not establish | 정의, 물성 계보(값마다 LIT/SCENARIO 표시), 유도, 자체 검증 4건, 말해 주지 않는 것 |
| `exact/db3_properties.py` | Geometry and properties with LIT/SCENARIO markers. **Standalone, numpy only** | 형상과 물성. LIT/SCENARIO 표시. **독립 실행, numpy 만** |
| `exact/db3_exact.py` | Reference implementation: layer transfer matrix + one scalar Newton. **Standalone** | 참조 구현 — 층 전달행렬 + 스칼라 Newton. **독립 실행** |
| `exact/run_reference.py` | Regenerates the reference values and checks them against four known limits. **Standalone** | 참조값 재생성 + 알려진 극한 4개로 자체 검사. **독립 실행** |
| `exact/check_report.py` | Grades a submitted report against the acceptance criterion. **Standalone** | 제출된 보고서를 합격 기준과 대조. **독립 실행** |
| `reference_values.json` | Generated reference numbers, three perfusion cases | 생성된 참조값, 관류 3경우 |
| `meshes/db3_rN.mesh.npz` | The h, h/2, h/4 meshes for `yuchiri-axirad2D` | 특정 솔버용 격자 |
| `meshes/db3_rN.mesh.txt` | The same meshes in plain text, **for any code** | 같은 격자의 평문판. **어떤 코드도 읽을 수 있다** |
| `meshes/MESH_FORMAT.md` | The plain-text format, with a reader in ~15 lines | 평문 형식과 15줄짜리 읽기 예 |
| `results/yuchiri-axirad2D_v2.0.json` | One report per code, in the suite schema | 코드마다 하나씩의 보고서 |
| `figures/db3_numerical_results.png` | Seven panels: exact comparison, convergence order, error distribution, Newton, 2D field, radial variation, summary | 7패널 — 정확해 대조, 수렴 차수, 오차 분포, Newton, 2차원 온도장, 반경 변화, 종합 |
| `figures/db3_biological_meaning.png` | Two panels: blood flow and surface temperature; the heat budget | 2패널 — 혈류와 표면 온도, 열수지 |
| `figures/make_numerical_figure.py` | Regenerates the numerical figure from a live solver run | 솔버를 실제로 돌려 도면 재생성 |
| `docs/results_guide.md` | How to read the numerical figure, panel by panel | 수치 결과 도면을 패널별로 읽는 법 |
| `docs/claims_and_coefficients.md` | **Report: which claims the coefficients support.** Separates the supported claim (radiation ≥ convection in still indoor air) from the unsupported one (radiation is 55 % of a person's heat loss) | **보고서 — 계수가 뒷받침하는 주장.** 성립하는 주장(정지 실내 공기에서 복사 ≥ 대류)과 성립하지 않는 주장(복사가 사람 열손실의 55 %)을 가른다 |
| `figures/db3_claims_and_coefficients.png` | The three-panel figure for that report | 그 보고서의 3패널 도면 |
| `figures/make_claims_figure.py` | Regenerates it; numpy + matplotlib only, no solver | 재생성 스크립트. numpy + matplotlib 만, 솔버 불필요 |
| `docs/biology_guide.md` | What the numbers mean biologically | 숫자의 생물학적 의미 |
