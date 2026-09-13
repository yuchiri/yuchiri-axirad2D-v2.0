# DB-3 — layered skin with perfusion and radiative surface loss
# DB-3 — 관류가 있는 다층 피부와 복사 표면 손실

This is the solver-side example. **The benchmark itself — problem definition,
derivation of the exact solution, reference values, meshes and the report
schema — lives in the separate repository `yuchiri-axibio-bench`.**

여기는 솔버 쪽 예제다. **벤치마크 본체 — 문제 정의, 정확해 유도, 참조값, 격자,
보고 형식 — 는 별도 저장소 `yuchiri-axibio-bench` 에 있다.**

Why separate: a benchmark that lives inside the solver it grades can only show
that the code agrees with itself.
분리하는 이유: 채점하는 벤치마크가 채점받는 솔버 안에 있으면 "코드가 자기 자신과
일치한다"는 것밖에 보이지 못한다.

## Run / 실행

```bash
export PYTHONPATH=src:examples:examples/db3
python examples/db3/db3_problem.py     # meshes + dimensionless groups
python examples/db3/db3_verify.py      # solve, compare with exact, order of convergence
```

## Files / 파일

| File | Contents |
|---|---|
| `db3_problem.py` | geometry, properties with provenance markers, mesh generation / 형상, 출처가 표시된 물성, 격자 생성 |
| `db3_exact.py` | exact solution: layer transfer matrix + one scalar Newton / 정확해: 층 전달행렬 + 스칼라 Newton |
| `db3_verify.py` | runs h, h/2, h/4 and reports the observed order / h·h/2·h/4 를 풀고 관측 차수를 보고 |
