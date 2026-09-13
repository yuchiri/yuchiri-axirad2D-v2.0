# Mesh format / 격자 형식

Each mesh is shipped twice.

| File | For |
|---|---|
| `db3_rN.mesh.npz` | NumPy archive, read by `yuchiri-axirad2D` |
| `db3_rN.mesh.txt` | **plain text, for any other code** |

격자는 두 벌로 배포한다. `.npz` 는 특정 솔버용이고, `.txt` 는 **어떤 코드도 읽을 수
있도록** 둔 것이다. 모음이 코드에 독립적이라고 말하려면 후자가 있어야 한다.

## Plain text layout / 평문 형식

```
NODES n
# id  r  z
0 0.0 0.0
...
ELEMENTS m
# id  n_nodes  material  q_vol[W/m^3]  node_ids...
0 9 subcutaneous 0 0 2 24 22 1 13 23 11 12
...
NSET core k
<k node ids on one line>
NSET surface k
<k node ids on one line>
```

* Units are metres; `r >= 0`; the geometry is axisymmetric, so `dV = 2*pi*r dr dz`.
* All elements here are **9-node Lagrange quadrilaterals**.
* **Local node ordering**: the four corners counter-clockwise first, then the four
  mid-side nodes in edge order (edge `e` joins corner `e` to corner `(e+1) mod 4`),
  then the centre node last.
* `q_vol` is zero throughout DB-3; the heat source is metabolic and is a property
  of the material, not of the element.
* 단위는 m, `r >= 0`, 축대칭이므로 `dV = 2πr dr dz`.
  요소는 전부 **9절점 Lagrange 사각형**이다.
  국소 절점 순서는 코너 4개를 반시계로 먼저, 그다음 중간절점 4개를 변 순서대로,
  마지막이 중심 절점이다.

## Refinement sequence / 세분 계열

`r1`, `r2`, `r4` are the `h`, `h/2`, `h/4` sequence required by the acceptance
criterion. The limiting length is the thinnest layer, the epidermis: element size
0.1, 0.05 and 0.025 mm.

합격 기준이 요구하는 `h`, `h/2`, `h/4` 계열이다. 지배적인 길이는 가장 얇은 층인
표피이며, 요소 크기가 0.1 / 0.05 / 0.025 mm 다.

## Reading it / 읽기 예

```python
def read_mesh(path):
    nodes, elems, nsets = [], [], {}
    with open(path) as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    i = 0
    while i < len(lines):
        head = lines[i].split(); i += 1
        if head[0] == "NODES":
            for _ in range(int(head[1])):
                p = lines[i].split(); i += 1
                nodes.append((float(p[1]), float(p[2])))
        elif head[0] == "ELEMENTS":
            for _ in range(int(head[1])):
                p = lines[i].split(); i += 1
                elems.append(dict(material=p[2], q_vol=float(p[3]),
                                  nodes=[int(x) for x in p[4:]]))
        elif head[0] == "NSET":
            nsets[head[1]] = [int(x) for x in lines[i].split()]; i += 1
    return nodes, elems, nsets
```
