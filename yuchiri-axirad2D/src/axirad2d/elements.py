# -*- coding: utf-8 -*-
"""[EN] Element shape functions and numerical quadrature.

Specification sections 5.3, 5.4, 11.  Five supported element types, identified
by node count: 3/6-node triangles and 4/8/9-node quadrilaterals.
Local node ordering is counter-clockwise, corners first, mid-side nodes after.

[KO] 요소 형상함수와 수치적분.

See USER_GUIDE sections 4.2 and 4.3 (element types, local node ordering).
공개 문서 USER_GUIDE 4.2·4.3절 참조.
지원 요소 5종 — 절점 수로 판별한다.

    3  삼각형 1차      4  사각형 1차
    6  삼각형 2차      8  사각형 2차 (Serendipity)
    9  사각형 2차 (Lagrange)

국소 절점 순서 — 반시계, 코너 먼저 · 중간절점 나중 (§5.4).
"""
from __future__ import annotations
import numpy as np

# ----------------------------------------------------------------------
# 요소 종류
# ----------------------------------------------------------------------
TRI3, QUAD4, TRI6, QUAD8, QUAD9 = 3, 4, 6, 8, 9
SUPPORTED = (TRI3, QUAD4, TRI6, QUAD8, QUAD9)

# 코너 절점 수
N_CORNER = {TRI3: 3, TRI6: 3, QUAD4: 4, QUAD8: 4, QUAD9: 4}
# 변의 개수 = 코너 수
N_EDGE = N_CORNER
IS_TRI = {TRI3: True, TRI6: True, QUAD4: False, QUAD8: False, QUAD9: False}
ORDER = {TRI3: 1, QUAD4: 1, TRI6: 2, QUAD8: 2, QUAD9: 2}


def edge_nodes(etype: int, e: int):
    """변 e 의 국소 절점 번호. (코너1, 코너2, 중간절점 또는 None)

    §5.4 — 변 e 는 코너 e 와 코너 (e+1) mod nc 를 잇는다.
    2차 요소의 중간절점은 코너 다음에 변 순서대로 온다.
    """
    nc = N_CORNER[etype]
    c1, c2 = e, (e + 1) % nc
    mid = nc + e if ORDER[etype] == 2 else None
    return c1, c2, mid


# ----------------------------------------------------------------------
# 형상함수  N(xi, eta),  dN/dxi,  dN/deta
# ----------------------------------------------------------------------
def shape(etype: int, xi, eta):
    """반환 (N, dNdxi, dNdeta), 각각 shape (nn,) 또는 (nn, npt)."""
    xi = np.asarray(xi, dtype=float)
    eta = np.asarray(eta, dtype=float)
    o = np.ones_like(xi)
    z = np.zeros_like(xi)

    if etype == TRI3:
        L1, L2, L3 = 1.0 - xi - eta, xi, eta
        N = np.array([L1, L2, L3])
        dNx = np.array([-o, o, z])
        dNe = np.array([-o, z, o])
        return N, dNx, dNe

    if etype == TRI6:
        L1, L2, L3 = 1.0 - xi - eta, xi, eta
        N = np.array([L1 * (2 * L1 - 1), L2 * (2 * L2 - 1), L3 * (2 * L3 - 1),
                      4 * L1 * L2, 4 * L2 * L3, 4 * L3 * L1])
        dL1x, dL2x, dL3x = -o, o, z
        dL1e, dL2e, dL3e = -o, z, o
        dNx = np.array([(4 * L1 - 1) * dL1x, (4 * L2 - 1) * dL2x, (4 * L3 - 1) * dL3x,
                        4 * (dL1x * L2 + L1 * dL2x), 4 * (dL2x * L3 + L2 * dL3x),
                        4 * (dL3x * L1 + L3 * dL1x)])
        dNe = np.array([(4 * L1 - 1) * dL1e, (4 * L2 - 1) * dL2e, (4 * L3 - 1) * dL3e,
                        4 * (dL1e * L2 + L1 * dL2e), 4 * (dL2e * L3 + L2 * dL3e),
                        4 * (dL3e * L1 + L3 * dL1e)])
        return N, dNx, dNe

    if etype == QUAD4:
        s = np.array([-1.0, 1.0, 1.0, -1.0])
        t = np.array([-1.0, -1.0, 1.0, 1.0])
        N, dNx, dNe = [], [], []
        for i in range(4):
            N.append(0.25 * (1 + s[i] * xi) * (1 + t[i] * eta))
            dNx.append(0.25 * s[i] * (1 + t[i] * eta))
            dNe.append(0.25 * t[i] * (1 + s[i] * xi))
        return np.array(N), np.array(dNx), np.array(dNe)

    if etype == QUAD9:
        # 1차원 Lagrange 3점  (-1, 0, +1)
        def l3(u):
            return np.array([0.5 * u * (u - 1), 1.0 - u * u, 0.5 * u * (u + 1)])

        def dl3(u):
            return np.array([u - 0.5, -2.0 * u, u + 0.5])
        Lx, Le = l3(xi), l3(eta)
        Dx, De = dl3(xi), dl3(eta)
        # 국소 (p, q):  p 는 xi 방향 index 0..2, q 는 eta 방향
        # §5.4 순서 -> (p,q):  0:(0,0) 1:(2,0) 2:(2,2) 3:(0,2)
        #                      4:(1,0) 5:(2,1) 6:(1,2) 7:(0,1) 8:(1,1)
        pq = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 0), (2, 1), (1, 2), (0, 1), (1, 1)]
        N = np.array([Lx[p] * Le[q] for p, q in pq])
        dNx = np.array([Dx[p] * Le[q] for p, q in pq])
        dNe = np.array([Lx[p] * De[q] for p, q in pq])
        return N, dNx, dNe

    if etype == QUAD8:
        s = np.array([-1.0, 1.0, 1.0, -1.0])
        t = np.array([-1.0, -1.0, 1.0, 1.0])
        N = [None] * 8
        dNx = [None] * 8
        dNe = [None] * 8
        for i in range(4):
            a, b = s[i] * xi, t[i] * eta
            N[i] = 0.25 * (1 + a) * (1 + b) * (a + b - 1)
            dNx[i] = 0.25 * s[i] * (1 + b) * (2 * a + b)
            dNe[i] = 0.25 * t[i] * (1 + a) * (a + 2 * b)
        # 중간절점 4:(0,1)변 -> eta=-1 ; 5:(1,2) -> xi=+1 ; 6:(2,3) -> eta=+1 ; 7:(3,0) -> xi=-1
        N[4] = 0.5 * (1 - xi * xi) * (1 - eta)
        dNx[4] = -xi * (1 - eta)
        dNe[4] = -0.5 * (1 - xi * xi)
        N[5] = 0.5 * (1 + xi) * (1 - eta * eta)
        dNx[5] = 0.5 * (1 - eta * eta)
        dNe[5] = -eta * (1 + xi)
        N[6] = 0.5 * (1 - xi * xi) * (1 + eta)
        dNx[6] = -xi * (1 + eta)
        dNe[6] = 0.5 * (1 - xi * xi)
        N[7] = 0.5 * (1 - xi) * (1 - eta * eta)
        dNx[7] = -0.5 * (1 - eta * eta)
        dNe[7] = -eta * (1 - xi)
        return np.array(N), np.array(dNx), np.array(dNe)

    raise ValueError("지원하지 않는 요소 절점 수: %r" % etype)


# ----------------------------------------------------------------------
# 수치적분
# ----------------------------------------------------------------------
def _gauss1d(n: int):
    x, w = np.polynomial.legendre.leggauss(n)
    return x, w


_TRI_RULES = {
    # (차수): (점 (xi, eta), 가중치)  가중치 합 = 1/2 (단위 삼각형 면적)
    1: (np.array([[1 / 3, 1 / 3]]), np.array([0.5])),
    2: (np.array([[1 / 6, 1 / 6], [2 / 3, 1 / 6], [1 / 6, 2 / 3]]),
        np.array([1 / 6, 1 / 6, 1 / 6])),
    4: (np.array([[0.44594849091597, 0.44594849091597],
                  [0.10810301816807, 0.44594849091597],
                  [0.44594849091597, 0.10810301816807],
                  [0.09157621350977, 0.09157621350977],
                  [0.81684757298046, 0.09157621350977],
                  [0.09157621350977, 0.81684757298046]]),
        np.array([0.111690794839005, 0.111690794839005, 0.111690794839005,
                  0.054975871827661, 0.054975871827661, 0.054975871827661])),
}


def quadrature(etype: int, bump: int = 0):
    """적분점과 가중치. bump 로 차수를 올릴 수 있다 (§11.3).

    반환 (xi, eta, w) — 각각 (npt,)
    """
    if IS_TRI[etype]:
        deg = {1: 1, 2: 2}[ORDER[etype]] + bump
        key = 1 if deg <= 1 else (2 if deg <= 2 else 4)
        pts, w = _TRI_RULES[key]
        return pts[:, 0].copy(), pts[:, 1].copy(), w.copy()
    n = ORDER[etype] + 1 + bump          # 1차 -> 2점, 2차 -> 3점
    x, w = _gauss1d(n)
    XI, ETA = np.meshgrid(x, x, indexing="ij")
    W = np.outer(w, w)
    return XI.ravel(), ETA.ravel(), W.ravel()


def edge_quadrature(order: int, bump: int = 0):
    """변 위의 1차원 적분점. 매개변수 u in [-1, 1]."""
    return _gauss1d(order + 1 + bump)


def edge_shape(etype: int, e: int, u):
    """변 e 위에서의 1차원 형상함수 값과 그 미분 (변 국소 절점 기준).

    반환 (idx, Nb, dNb)  — idx 는 요소 국소 절점 번호 목록
    """
    c1, c2, mid = edge_nodes(etype, e)
    u = np.asarray(u, dtype=float)
    if mid is None:
        return [c1, c2], np.array([0.5 * (1 - u), 0.5 * (1 + u)]), \
            np.array([-0.5 * np.ones_like(u), 0.5 * np.ones_like(u)])
    return [c1, c2, mid], \
        np.array([0.5 * u * (u - 1), 0.5 * u * (u + 1), 1.0 - u * u]), \
        np.array([u - 0.5, u + 0.5, -2.0 * u])
