# BM — 동축 원통 밀폐공동

## 실행

```bash
cd <repo>
export PYTHONPATH=src
python examples/coaxial_enclosure/build_mesh.py     # 격자 생성 (외부 도구 역할)
python -m axirad2d.cli examples/coaxial_enclosure/case.toml
PYTHONPATH=src:examples python examples/coaxial_enclosure/reference.py
```

## 파일

| 파일 | 역할 |
|---|---|
| `build_mesh.py` | 격자 생성. **솔버의 일부가 아니다.** 외부 메셔 역할 |
| `case.toml` | 문제 정의 — 물성, 경계조건, 복사·해법 제어 |
| `coaxial_enclosure.mesh.npz` | 격자 파일 (절점·요소·재료·발열·절점집합) |
| `reference.py` | 해석 참조값 계산과 대조 |
| `out/` | 결과와 진단 |

## 왜 이 형상인가

내부물체가 **볼록**하고 공동에 **완전히 포위**되므로 `F(1→1)=0`, `F(1→2)=1` 이
기하학적 사실만으로 성립한다. 형상계수표를 인용할 필요가 없다.

공동벽을 흑체로 두면 정확해는

```
Q = ε₁ A₁ σ (T₁⁴ − T₂⁴)
```

이며 **어떤 근사도 없다**.

## 실측

```
T₁ = 564.6711 K   (정확해 564.6606 K,  +0.0019 %)
Q  = 200.0162 W   (투입 200 W,          +0.0081 %)
Newton 2차 수렴: 2.19e-1 → 6.87e-2 → 4.01e-3 → 1.15e-5 → 9.21e-11
```

## ⚠ 회색벽 2면 집중식을 기준으로 쓰지 말 것

집중식은 각 면의 복사도가 균일하다고 가정한다. 공동벽은 부위마다 조사량이
다르므로 성립하지 않는다. ε₂=0.6 에서 약 1.6 % 차이가 나고 **광선 수를 늘려도
줄지 않는다**(계통 편차). ε₂=1.0 에서는 0.005 % 로 떨어진다.
자세한 내용은 `reference.py` 주석 참조.
