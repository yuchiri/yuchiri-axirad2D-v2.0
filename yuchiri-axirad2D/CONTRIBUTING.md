# Contributing / 기여 안내

*English first · 한국어는 아래에 이어집니다*

---
---

# English

## Read this first

This code is the result of applying **"fail loudly, never silently"**
consistently. The principles below are not stylistic preferences but the
skeleton of the design. **Changes that break them will not be accepted.**

| # | Principle | Concretely |
|---|---|---|
| 1 | **No auto-correction** | Do not renormalise closure `Σ B_ab` to 1. Do not symmetrise reciprocity. Do not auto-fix node ordering |
| 2 | **No switch disables a check** | Do not add a bypass to the normal cross-check, mesh checks G1/G2/G4, the leakage check, or the environment-radiation overlap check |
| 3 | **Abort, but leave diagnostics** | Every abort records the cause, the location and the numbers in the diagnostics file |
| 4 | **No unjustified constants** | If you need a new threshold, **first look for a structure in which the check works without one.** If you cannot find it, document how the value is derived |
| 5 | **Normals are not inherited from endpoint order** | Determined topologically, cross-checked geometrically |
| 6 | **No geometry or material numbers in the code** | Geometry, mesh, materials, heat sources and boundary conditions are all input. Example numbers stay inside `examples/` |
| 7 | **Do not break reproducibility** | Serial and MPI results must be bit-for-bit identical. Ray random numbers must be deterministic in (segment, bounce) |

Worked examples of principle 4 — the G4 tolerance is not a fixed constant but
`64 × n_elem × ε_machine`, **derived from the number of terms**. Duplicate nodes
are judged only by **bitwise identical coordinates**, not by a distance
threshold. If the maximum bounce count is too small, the **leakage check catches
it automatically**.

## Before you change anything

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5
python -m pytest tests -q          # all 63 must pass
```

If you touched radiation, assembly or the solver, re-run the benchmarks:

```bash
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python examples/coaxial_enclosure/reference.py
python examples/bm2_bm5/verify.py
```

If you touched MPI, verify bit-for-bit reproducibility yourself
(`docs/USER_GUIDE.md` §9.2).

## Claim audit — before any release

Three times in this project a document has promised behaviour the code did not
have: bit-for-bit MPI reproducibility, the P3 shape-bias diagnostic, and the
detailed-output arrays. Each time the gap was silent, because nothing tested the
document.

**Before tagging a release, walk every public document and, for each stated
behaviour, name the test or the output that demonstrates it.** If you cannot name
one, either implement it or change the sentence. Two tests
(`test_documented_detail_arrays_are_actually_written`,
`test_documented_diagnostics_keys_exist`) pin the output side of this; the rest is
a reading task and has to be done by a person.

## Please state in the pull request

1. What you changed
2. How you confirmed none of the seven principles is violated
3. If you introduced a new threshold, **how its value is derived**
4. Test results (63 tests plus the relevant benchmarks)

## If you add a benchmark

* Compute the reference **directly from a published expression.** Do not
  reproduce a numerical table from a publication.
* Prefer an **exact** solution over an approximation — convex body fully
  enclosed, closed-form view factors, uniform irradiation by symmetry, etc.
* **Do not use the lumped two-surface gray formula as the target.** It assumes
  uniform radiosity and does not hold for general geometry
  (`docs/BENCHMARK_RESULTS.md` §7).

## Out of scope

The following are deliberately excluded. Requests are welcome but there is no
plan to implement them.

* Mesh generation
* Participating-media radiation (absorption / scattering)
* Anisotropic properties
* Fluid flow and mass transfer
* Phase change and latent heat

---
---

# 한국어

## 먼저 알아 둘 것

이 코드는 **"조용히 틀리느니 멈춘다"** 를 일관되게 적용한 결과물이다.
아래 원칙은 취향이 아니라 설계의 뼈대이며, 이를 깨는 변경은 받지 않는다.

| # | 원칙 | 구체적으로 |
|---|---|---|
| 1 | **자동 보정을 하지 않는다** | 폐쇄성 `Σ B_ab` 를 1 로 정규화하지 않는다. 상반성을 대칭화하지 않는다. 절점 순서를 자동 교정하지 않는다 |
| 2 | **검사를 끄는 스위치를 두지 않는다** | 법선 교차검증, 격자 검증 G1·G2·G4, 누출 검사, 환경 복사 중첩 검사에 우회 경로를 만들지 않는다 |
| 3 | **중단하되 진단은 남긴다** | 어떤 중단도 원인·위치·수치를 진단 파일에 기록한다 |
| 4 | **근거 없는 상수를 도입하지 않는다** | 새 임계값이 필요하면, 먼저 **임계값 없이 검사가 성립하는 구조**를 찾아라. 못 찾으면 그 값의 유도 근거를 문서화하라 |
| 5 | **법선을 끝점 순서에서 상속받지 않는다** | 위상으로 정하고 기하로 교차검증한다 |
| 6 | **형상·물성 수치를 코드에 넣지 않는다** | 형상·격자·물성·열원·경계조건은 전부 입력이다. 예제의 수치도 `examples/` 밖으로 나가지 않는다 |
| 7 | **재현성을 깨지 않는다** | 직렬과 MPI 결과가 비트 단위로 같아야 한다. 광선 난수는 (세그먼트, 반사 횟수)로 결정론적이어야 한다 |

원칙 4 의 실제 예 — G4 허용오차는 고정 상수가 아니라 `64 × 요소수 × 기계정밀도`
로 **항의 개수에서** 유도했다. 절점 중복은 거리 임계값 대신 **비트 단위 동일 좌표**
로만 판정한다. 최대 반사 횟수는 값이 부족하면 누출 검사가 **자동으로 잡아낸다.**

## 변경 전 확인

```bash
export PYTHONPATH=src:examples:examples/coaxial_enclosure:examples/bm2_bm5
python -m pytest tests -q          # 63건 전부 통과해야 한다
```

복사·조립·해법을 건드렸다면 벤치마크도 다시 돌려라.

```bash
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
python examples/coaxial_enclosure/reference.py
python examples/bm2_bm5/verify.py
```

MPI 를 건드렸다면 비트 단위 재현성을 직접 확인하라 (`docs/USER_GUIDE.md` 9.2절).

## 주장 감사 — 릴리스 전마다

이 프로젝트에서 문서가 코드에 없는 동작을 약속한 일이 **세 번** 있었다. MPI 비트
단위 재현성, P3 형상 편차 진단, 상세 출력 배열. 세 번 모두 격차가 조용했다.
**문서를 시험하는 것이 아무것도 없었기 때문이다.**

**릴리스 태그를 붙이기 전에 공개 문서를 전부 훑고, 문서가 적은 동작마다 그것을
보이는 시험이나 출력을 지목하라.** 지목할 수 없으면 구현하거나 문장을 고쳐라.
출력 쪽은 시험 2건(`test_documented_detail_arrays_are_actually_written`,
`test_documented_diagnostics_keys_exist`)이 고정하지만, 나머지는 읽는 일이며
사람이 해야 한다.

## PR 에 적어 주십시오

1. 무엇을 바꿨는가
2. 위 원칙 7개 중 어느 것에도 저촉되지 않음을 어떻게 확인했는가
3. 새 임계값을 도입했다면 그 값의 **유도 근거**
4. 시험 결과 (63건 + 관련 벤치마크)

## 새 벤치마크를 추가한다면

* 참조값은 **공개된 수식으로 직접 계산**하라. 문헌의 수치표를 복제하지 마라.
* 가능하면 **근사식이 아니라 정확해**를 근거로 삼아라.
  볼록체 완전 포위, 닫힌 형태 형상계수, 대칭성에 의한 균일 조사량 등.
* **회색벽 2면 집중식을 기준으로 쓰지 마라.** 그 식은 복사도 균일을 가정하며
  일반 형상에서 성립하지 않는다 (`docs/BENCHMARK_RESULTS.md` 7절).

## 하지 않을 것

아래는 의도적으로 범위 밖이다. 요청은 받되 구현 계획은 없다.

* 격자 생성기
* 참여 매질 복사 (흡수·산란)
* 이방성 물성
* 유동·물질전달
* 상변화·잠열
