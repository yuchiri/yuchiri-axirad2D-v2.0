# -*- coding: utf-8 -*-
"""[EN] Automatic radiating-surface extraction, enclosure decomposition and
normal determination.

Specification sections 10.2-10.4.  Normals are determined topologically and
cross-checked geometrically; a mismatch aborts.

[KO] 복사면 자동 추출, enclosure 분해, 법선 판정.

See USER_GUIDE sections 8.1 and 8.2 (radiating surfaces, normals).
공개 문서 USER_GUIDE 8.1·8.2절 참조.
"""
from __future__ import annotations
import numpy as np
from . import elements as E
from .mesh import Mesh


class SurfaceError(Exception):
    """복사면 추출 오류. 끄는 스위치 없이 중단한다 (CONTRIBUTING 원칙 2).

    Surface extraction error. No switch disables this (CONTRIBUTING, principle 2).
    """


class Segments:
    """복사면 세그먼트 모음.

    n1, n2   (ns,)  코너 절점 번호  (§10.10 — 중간절점은 쓰지 않는다)
    P1, P2   (ns,2) 끝점 (r, z)
    area     (ns,)  원뿔대 측면적 [m^2]
    eps      (ns,)  방사율
    nrm      (ns,2) 단위 법선 (투명 영역 쪽)
    encl     (ns,)  enclosure 번호
    elem     (ns,)  세그먼트를 만든 투명 요소 번호
    ledge    (ns,)  그 요소 안에서의 국소 변 번호
    owner    (ns,)  세그먼트를 소유한 불투명 재료 이름 (경계면은 '__boundary__')
    """

    def __init__(self):
        for k in ("n1", "n2", "eps", "encl", "elem", "ledge"):
            setattr(self, k, np.zeros(0))
        self.P1 = np.zeros((0, 2))
        self.P2 = np.zeros((0, 2))
        self.nrm = np.zeros((0, 2))
        self.area = np.zeros(0)
        self.owner = []

    def __len__(self):
        return len(self.area)


def _elem_centroid(mesh: Mesh, e: int):
    C = mesh.nodes[mesh.elems[e][:E.N_CORNER[mesh.etype[e]]]]
    return C.mean(axis=0)


def extract(mesh: Mesh, materials: dict, boundary_emissivity: float,
            report: dict | None = None) -> Segments:
    """투명/불투명 경계에서 복사면을 자동 추출한다 (§10.2).

    boundary_emissivity — 투명 요소가 도메인 경계와 접하는 변의 방사율.
    """
    rep = {} if report is None else report
    transparent = np.array([not materials[m].opaque for m in mesh.emat])

    # --- enclosure = 투명 요소의 연결 성분 -----------------------------
    label = -np.ones(mesh.ne, dtype=np.int64)
    ed = mesh.edges()
    adj = {e: [] for e in range(mesh.ne) if transparent[e]}
    for lst in ed.values():
        if len(lst) == 2:
            a, b = lst[0][0], lst[1][0]
            if transparent[a] and transparent[b]:
                adj[a].append(b)
                adj[b].append(a)
    nlab = 0
    for e in range(mesh.ne):
        if not transparent[e] or label[e] >= 0:
            continue
        stack = [e]
        label[e] = nlab
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if label[v] < 0:
                    label[v] = nlab
                    stack.append(v)
        nlab += 1

    # --- 세그먼트 수집 --------------------------------------------------
    n1s, n2s, epss, encls, nrms, owners = [], [], [], [], [], []
    elems, ledges = [], []          # 소유 요소와 그 국소 변 — 곡선 변 면적 비교용
    zero_area = 0
    mismatch = []
    for key, lst in ed.items():
        if len(lst) == 2:
            (ea, la), (eb, lb) = lst
            ta, tb = transparent[ea], transparent[eb]
            if ta == tb:
                continue                       # 투명-투명 또는 불투명-불투명
            if ta:
                etr, ltr, eop = ea, la, eb
            else:
                etr, ltr, eop = eb, lb, ea
            owner = str(mesh.emat[eop])
            eps = float(materials[owner].emissivity)
        else:
            (ea, la), = lst
            if not transparent[ea]:
                continue                       # 불투명체의 외곽면은 복사면이 아니다
            etr, ltr = ea, la
            owner = "__boundary__"
            eps = float(boundary_emissivity)

        a, b, _ = mesh.edge_node_ids(etr, ltr)   # 투명 요소의 국소 순서 = 반시계
        Pa, Pb = mesh.nodes[a], mesh.nodes[b]
        L = np.hypot(Pb[0] - Pa[0], Pb[1] - Pa[1])
        area = np.pi * (Pa[0] + Pb[0]) * L
        if area <= 0.0:
            zero_area += 1
            continue

        # 1차 판정 — 위상. 반시계 요소의 변에서 내부는 진행방향 왼쪽.
        t = Pb - Pa
        n_topo = np.array([-t[1], t[0]])
        n_topo = n_topo / np.linalg.norm(n_topo)
        # 2차 판정 — 기하. 중점에서 투명 요소 중심 방향.
        n_geom = _elem_centroid(mesh, etr) - 0.5 * (Pa + Pb)
        ng = np.linalg.norm(n_geom)
        n_geom = n_geom / ng if ng > 0 else n_topo
        if float(n_topo @ n_geom) <= 0.0:
            mismatch.append(dict(elem=int(etr), local_edge=int(ltr),
                                 nodes=(int(a), int(b)),
                                 P1=Pa.tolist(), P2=Pb.tolist(),
                                 n_topo=n_topo.tolist(), n_geom=n_geom.tolist()))
        n1s.append(a)
        n2s.append(b)
        elems.append(int(etr))
        ledges.append(int(ltr))
        epss.append(eps)
        encls.append(int(label[etr]))
        nrms.append(n_topo)
        owners.append(owner)

    rep["enclosure_count"] = nlab
    rep["segment_count"] = len(n1s)
    rep["zero_area_segments"] = zero_area
    rep["normal_mismatch"] = mismatch
    if mismatch:
        raise SurfaceError(
            "§10.4 법선 교차검증 실패 — 불일치 세그먼트 %d 개. "
            "진단의 normal_mismatch 를 보라." % len(mismatch))

    S = Segments()
    S.n1 = np.asarray(n1s, dtype=np.int64)
    S.n2 = np.asarray(n2s, dtype=np.int64)
    S.P1 = mesh.nodes[S.n1] if len(n1s) else np.zeros((0, 2))
    S.P2 = mesh.nodes[S.n2] if len(n2s) else np.zeros((0, 2))
    S.eps = np.asarray(epss, dtype=float)
    S.encl = np.asarray(encls, dtype=np.int64)
    S.nrm = np.asarray(nrms, dtype=float).reshape(-1, 2)
    S.owner = owners
    S.elem = np.asarray(elems, dtype=np.int64)
    S.ledge = np.asarray(ledges, dtype=np.int64)
    L = np.hypot(S.P2[:, 0] - S.P1[:, 0], S.P2[:, 1] - S.P1[:, 1])
    S.area = np.pi * (S.P1[:, 0] + S.P2[:, 0]) * L
    rep["enclosure_area"] = [float(S.area[S.encl == i].sum()) for i in range(nlab)]
    rep["enclosure_segments"] = [int((S.encl == i).sum()) for i in range(nlab)]
    return S
