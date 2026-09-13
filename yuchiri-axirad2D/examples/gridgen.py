# -*- coding: utf-8 -*-
"""구조 격자 생성기.

★ 이것은 yuchiri-axirad2D 솔버의 일부가 아니다. 예제 격자를 만드는 보조 도구다.
솔버는 격자를 만들지 않는다. 격자는 외부에서 온다 (README).
이 스크립트가 그 '외부' 역할을 한다.
"""
from __future__ import annotations
import numpy as np


def structured_quad9(redges, zedges, nr, nz, material_fn, qvol_fn=None):
    """직교 밴드로 9절점 사각형 격자를 만든다.

    redges, zedges : 밴드 경계
    nr, nz         : 밴드별 분할수
    material_fn(rc, zc) -> 재료 이름
    반환 dict(nodes, elems, emat, qvol, rline, zline)
    """
    def line(edges, n):
        out = [edges[0]]
        for i in range(len(n)):
            seg = np.linspace(edges[i], edges[i + 1], 2 * n[i] + 1)
            out.extend(seg[1:])
        return np.array(out)

    R = line(redges, nr)
    Z = line(zedges, nz)
    NR, NZ = len(R), len(Z)
    nodes = np.stack(np.meshgrid(R, Z, indexing="ij"), axis=-1).reshape(-1, 2)

    def nid(i, j):
        return j * NR + i
    # 위 배열은 (i, j) -> i*NZ + j 이므로 다시 만든다
    nodes = np.zeros((NR * NZ, 2))
    for j in range(NZ):
        for i in range(NR):
            nodes[nid(i, j)] = (R[i], Z[j])

    NRE, NZE = sum(nr), sum(nz)
    elems, emat, qvol = [], [], []
    for b in range(NZE):
        for a in range(NRE):
            i0, j0 = 2 * a, 2 * b
            # §5.4 반시계, 코너 먼저
            c = [nid(i0, j0), nid(i0 + 2, j0), nid(i0 + 2, j0 + 2), nid(i0, j0 + 2),
                 nid(i0 + 1, j0), nid(i0 + 2, j0 + 1), nid(i0 + 1, j0 + 2),
                 nid(i0, j0 + 1), nid(i0 + 1, j0 + 1)]
            elems.append(np.array(c, dtype=np.int64))
            rc = 0.5 * (R[i0] + R[i0 + 2])
            zc = 0.5 * (Z[j0] + Z[j0 + 2])
            m = material_fn(rc, zc)
            emat.append(m)
            qvol.append(0.0 if qvol_fn is None else float(qvol_fn(rc, zc, m)))
    return dict(nodes=nodes, elems=elems, emat=np.array(emat, dtype=object),
                qvol=np.array(qvol), rline=R, zline=Z, nid=nid, NR=NR, NZ=NZ)


def structured_quad9_mapped(uedges, vedges, nu, nv, mapfn, material_fn,
                            qvol_fn=None):
    """(u, v) 논리 격자를 mapfn 으로 (r, z) 에 사상해 9절점 격자를 만든다.

    mapfn(u, v) -> (r, z)
    코너 순서는 반시계가 되도록 자동으로 맞춘다 (§5.4).
    """
    def line(edges, n):
        out = [edges[0]]
        for i in range(len(n)):
            seg = np.linspace(edges[i], edges[i + 1], 2 * n[i] + 1)
            out.extend(seg[1:])
        return np.array(out)

    U, V = line(uedges, nu), line(vedges, nv)
    NU, NV = len(U), len(V)

    def nid(i, j):
        return j * NU + i

    nodes = np.zeros((NU * NV, 2))
    for j in range(NV):
        for i in range(NU):
            nodes[nid(i, j)] = mapfn(U[i], V[j])

    def corners(i0, j0, flip):
        if not flip:
            return [(i0, j0), (i0 + 2, j0), (i0 + 2, j0 + 2), (i0, j0 + 2)]
        return [(i0, j0), (i0, j0 + 2), (i0 + 2, j0 + 2), (i0 + 2, j0)]

    def signed_area(cs):
        P = np.array([nodes[nid(i, j)] for i, j in cs])
        return 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1)
                            - np.roll(P[:, 0], -1) * P[:, 1])

    flip = signed_area(corners(0, 0, False)) < 0.0

    NUE, NVE = sum(nu), sum(nv)
    elems, emat, qvol = [], [], []
    for b in range(NVE):
        for a in range(NUE):
            i0, j0 = 2 * a, 2 * b
            cs = corners(i0, j0, flip)
            mids = [((cs[k][0] + cs[(k + 1) % 4][0]) // 2,
                     (cs[k][1] + cs[(k + 1) % 4][1]) // 2) for k in range(4)]
            c = [nid(i, j) for i, j in cs] + [nid(i, j) for i, j in mids] \
                + [nid(i0 + 1, j0 + 1)]
            elems.append(np.array(c, dtype=np.int64))
            uc = 0.5 * (U[i0] + U[i0 + 2])
            vc = 0.5 * (V[j0] + V[j0 + 2])
            m = material_fn(uc, vc)
            emat.append(m)
            qvol.append(0.0 if qvol_fn is None else float(qvol_fn(uc, vc, m)))
    return dict(nodes=nodes, elems=elems, emat=np.array(emat, dtype=object),
                qvol=np.array(qvol), U=U, V=V, nid=nid, NU=NU, NV=NV, flip=flip)
