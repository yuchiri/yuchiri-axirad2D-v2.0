# -*- coding: utf-8 -*-
"""[EN] Gebhart absorption factors by Monte Carlo ray tracing.

Specification sections 10.5-10.8.  Key properties: batch invariance (random
numbers are deterministic in (segment, bounce) and indexed by ray id); closure
is never renormalised; reciprocity is never symmetrised.

[KO] 몬테카를로 광선 추적으로 Gebhart 흡수계수를 구한다.

See USER_GUIDE sections 8.3 and 8.4 (Gebhart factors, leakage).
공개 문서 USER_GUIDE 8.3·8.4절 참조.

핵심 성질
  * 배치 불변성 (§10.6) — 난수를 (세그먼트, 반사횟수) 로 결정론적으로 정하고
    광선 index 로 색인한다. 광선을 어떻게 나누어도 결과가 비트 단위로 같다.
  * 폐쇄성 자동 보정을 하지 않는다 (§10.7). 누출은 누출로 남는다.
  * 상반성 대칭화를 하지 않는다 (§10.8).
"""
from __future__ import annotations
import numpy as np
from .surfaces import Segments

_TOL = 1e-12


class RadiationError(Exception):
    pass


# ----------------------------------------------------------------------
class _Geo:
    """세그먼트의 교차 판정용 사전 계산."""

    def __init__(self, S: Segments):
        r1, z1 = S.P1[:, 0].copy(), S.P1[:, 1].copy()
        r2, z2 = S.P2[:, 0].copy(), S.P2[:, 1].copy()
        self.ns = len(r1)
        self.is_disk = np.abs(z2 - z1) < 1e-14
        dz = np.where(self.is_disk, 1.0, z2 - z1)
        self.B = np.where(self.is_disk, 0.0, (r2 - r1) / dz)
        self.A = np.where(self.is_disk, 0.0, r1 - self.B * z1)
        self.zc = z1                       # 원판의 z
        self.zmin = np.minimum(z1, z2)
        self.zmax = np.maximum(z1, z2)
        self.rmin = np.minimum(r1, r2)
        self.rmax = np.maximum(r1, r2)
        self.nr = S.nrm[:, 0].copy()
        self.nz = S.nrm[:, 1].copy()
        self.r1, self.z1, self.r2, self.z2 = r1, z1, r2, z2
        # 형상 허용오차 — 세그먼트 길이 규모에서 유도
        L = np.hypot(r2 - r1, z2 - z1)
        self.pad = 1e-9 * np.maximum(L, 1e-12)


def _intersect(P, D, G: _Geo, sub):
    """가장 가까운 교차 세그먼트를 찾는다.

    P, D : (m, 3)    sub : (k,) 후보 세그먼트 index
    반환 (tmin (m,), jhit (m,) — 없으면 -1)
    """
    m = P.shape[0]
    Px, Py, Pz = P[:, 0:1], P[:, 1:2], P[:, 2:3]
    Dx, Dy, Dz = D[:, 0:1], D[:, 1:2], D[:, 2:3]
    A = G.A[sub][None, :]
    B = G.B[sub][None, :]
    zc = G.zc[sub][None, :]
    zmin = G.zmin[sub][None, :] - G.pad[sub][None, :]
    zmax = G.zmax[sub][None, :] + G.pad[sub][None, :]
    rmin = G.rmin[sub][None, :] - G.pad[sub][None, :]
    rmax = G.rmax[sub][None, :] + G.pad[sub][None, :]
    disk = G.is_disk[sub][None, :]

    big = np.inf
    tbest = np.full((m, len(sub)), big)

    # --- 원판 -----------------------------------------------------------
    with np.errstate(divide="ignore", invalid="ignore"):
        td = (zc - Pz) / Dz
    xd = Px + td * Dx
    yd = Py + td * Dy
    rr = np.sqrt(xd * xd + yd * yd)
    okd = disk & np.isfinite(td) & (td > _TOL) & (rr >= rmin) & (rr <= rmax)
    tbest = np.where(okd, td, tbest)

    # --- 원뿔대 / 원통 ---------------------------------------------------
    aq = Dx * Dx + Dy * Dy - (B * Dz) ** 2
    Rp = A + B * Pz
    bq = 2.0 * (Px * Dx + Py * Dy - B * Dz * Rp)
    cq = Px * Px + Py * Py - Rp * Rp
    disc = bq * bq - 4.0 * aq * cq
    lin = np.abs(aq) < 1e-300
    with np.errstate(divide="ignore", invalid="ignore"):
        sq = np.sqrt(np.maximum(disc, 0.0))
        t1 = (-bq - sq) / (2.0 * aq)
        t2 = (-bq + sq) / (2.0 * aq)
        tl = -cq / bq
    for tt in (t1, t2, np.where(lin, tl, np.inf)):
        with np.errstate(invalid="ignore", over="ignore"):
            Z = Pz + tt * Dz
            Rz = A + B * Z
        ok = (~disk) & np.isfinite(tt) & (tt > _TOL) & (disc >= 0.0) \
            & (Z >= zmin) & (Z <= zmax) & (Rz >= -1e-14)
        tbest = np.where(ok & (tt < tbest), tt, tbest)

    j = np.argmin(tbest, axis=1)
    tmin = tbest[np.arange(m), j]
    hit = np.where(np.isfinite(tmin), sub[j], -1)
    return tmin, hit


def _basis(n):
    """n (m,3) 단위벡터에 대한 정규직교 접선 기저 (t1, t2)."""
    a = np.zeros_like(n)
    k = np.argmin(np.abs(n), axis=1)
    a[np.arange(len(n)), k] = 1.0
    t1 = np.cross(n, a)
    t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
    t2 = np.cross(n, t1)
    return t1, t2


def _rand(seed, seg, bounce, n, cols=4):
    """(세그먼트, 반사) 로 결정되는 난수 배열 (n, cols). 배치 불변 (§10.6)."""
    g = np.random.Generator(np.random.Philox(
        key=np.uint64(seed),
        counter=[np.uint64(seg), np.uint64(bounce), np.uint64(0), np.uint64(0)]))
    return g.random((n, cols))


def gebhart(S: Segments, n_ray: int = 20000, seed: int = 12345,
            n_bounce_max: int = 20, leak_tol: float = 1.0e-5,
            seg_subset=None, report: dict | None = None):
    """Gebhart 흡수계수 B[a, b] 를 구한다.

    seg_subset — MPI 에서 이 랭크가 담당할 소스 세그먼트 index. None 이면 전부.
    """
    rep = {} if report is None else report
    ns = len(S)
    G = _Geo(S)
    B = np.zeros((ns, ns))
    leak_open = np.zeros(ns, dtype=np.int64)
    leak_bounce = np.zeros(ns, dtype=np.int64)
    todo = np.arange(ns) if seg_subset is None else np.asarray(seg_subset)

    # enclosure 별 후보 세그먼트
    subs = {int(e): np.where(S.encl == e)[0] for e in np.unique(S.encl)}

    for a in todo:
        sub = subs[int(S.encl[a])]
        rnd = _rand(seed, a, 0, n_ray)
        # --- 방출점: 면적 가중 (dA ∝ r dl) --------------------------
        r1, z1 = S.P1[a]
        r2, z2 = S.P2[a]
        dr = r2 - r1
        if abs(dr) < 1e-15:
            u = rnd[:, 0]
        else:
            # CDF(u) = (r1 u + dr u^2/2) / ((r1+r2)/2)
            aa = 0.5 * dr
            bb = r1
            cc = -rnd[:, 0] * 0.5 * (r1 + r2)
            u = (-bb + np.sqrt(np.maximum(bb * bb - 4 * aa * cc, 0.0))) / (2 * aa)
            u = np.clip(u, 0.0, 1.0)
        rr = r1 + u * dr
        zz = z1 + u * (z2 - z1)
        phi = 2.0 * np.pi * rnd[:, 1]
        cp, sp = np.cos(phi), np.sin(phi)
        P = np.stack([rr * cp, rr * sp, zz], axis=1)
        nn = np.stack([G.nr[a] * cp, G.nr[a] * sp, np.full(n_ray, G.nz[a])], axis=1)
        # --- 확산 방출 방향 (cos 가중) --------------------------------
        t1, t2 = _basis(nn)
        st = np.sqrt(rnd[:, 2])                 # sin(theta) = sqrt(xi)
        ct = np.sqrt(np.maximum(1.0 - rnd[:, 2], 0.0))
        ph2 = 2.0 * np.pi * rnd[:, 3]
        D = (st * np.cos(ph2))[:, None] * t1 + (st * np.sin(ph2))[:, None] * t2 \
            + ct[:, None] * nn
        P = P + 1e-10 * nn

        idx = np.arange(n_ray)
        for bounce in range(n_bounce_max + 1):
            tmin, hit = _intersect(P, D, G, sub)
            alive = hit >= 0
            leak_open[a] += int((~alive).sum())
            idx, hit, tmin = idx[alive], hit[alive], tmin[alive]
            P, D = P[alive], D[alive]
            if len(idx) == 0:
                break
            P = P + tmin[:, None] * D
            if bounce == n_bounce_max:
                leak_bounce[a] += len(idx)
                break
            rb = _rand(seed, a, bounce + 1, n_ray, 3)
            absorbed = rb[idx, 0] < S.eps[hit]
            np.add.at(B[a], hit[absorbed], 1.0)
            keep = ~absorbed
            idx, hit, P, D = idx[keep], hit[keep], P[keep], D[keep]
            if len(idx) == 0:
                break
            # --- 확산 반사 ------------------------------------------
            ph = np.arctan2(P[:, 1], P[:, 0])
            cp, sp = np.cos(ph), np.sin(ph)
            nn = np.stack([G.nr[hit] * cp, G.nr[hit] * sp, G.nz[hit]], axis=1)
            t1, t2 = _basis(nn)
            st = np.sqrt(rb[idx, 1])
            ct = np.sqrt(np.maximum(1.0 - rb[idx, 1], 0.0))
            ph2 = 2.0 * np.pi * rb[idx, 2]
            D = (st * np.cos(ph2))[:, None] * t1 + (st * np.sin(ph2))[:, None] * t2 \
                + ct[:, None] * nn
            P = P + 1e-10 * nn
        B[a] /= float(n_ray)

    rep["seed"] = int(seed)
    rep["n_bounce_max"] = int(n_bounce_max)
    rep["leak_tol"] = float(leak_tol)
    if seg_subset is None:
        _diagnose(S, B, leak_open, leak_bounce, n_ray, leak_tol, rep)
    return B, leak_open, leak_bounce


def _diagnose(S, B, leak_open, leak_bounce, n_ray, leak_tol, rep):
    ns = len(S)
    tot = float(n_ray) * ns
    lo = leak_open.sum() / tot
    lb = leak_bounce.sum() / tot
    rep["n_ray"] = int(n_ray)
    rep["leak_open"] = lo
    rep["leak_bounce"] = lb
    rep["closure_min"] = float(B.sum(axis=1).min())
    rep["closure_max"] = float(B.sum(axis=1).max())
    # 상반성 (§10.8).  임계값을 쓰지 않는 지표 3종을 함께 보고한다.
    #   max_rel  — 성분별 상대오차의 최대. 가장 엄격하나 미세 성분에서 1 로 포화한다
    #   max_abs  — 최대 비대칭 / 전체 최대. 규모 정규화
    #   l1       — sum|L - L^T| / sum|L|.  전역 지표. N^(-1/2) 로 감소한다
    w = S.eps * S.area
    Lmat = w[:, None] * B
    num = np.abs(Lmat - Lmat.T)
    den = np.maximum(np.abs(Lmat), np.abs(Lmat.T))
    m = den > 0
    rep["reciprocity_max_rel"] = float((num[m] / den[m]).max()) if m.any() else 0.0
    rep["reciprocity_max_abs"] = float(num.max() / max(np.abs(Lmat).max(), 1e-300))
    rep["reciprocity_l1"] = float(num.sum() / max(np.abs(Lmat).sum(), 1e-300))
    rep["negative_B"] = int((B < 0).sum())
    if max(lo, lb) > leak_tol:
        raise RadiationError(
            "§10.7 누출 검사 실패 — 열린 형상 %.3e, 반사 초과 %.3e, 허용 %.3e. "
            "폐쇄성 보정을 하지 않으므로 실행을 중단한다." % (lo, lb, leak_tol))
