# -*- coding: utf-8 -*-
"""[EN] Mesh container, topology and validation.

Specification sections 5 and 9.  The code never generates a mesh; the mesh is
entirely external input.  Checks G1 (Jacobian), G2 (area cross-check) and
G4 (divergence theorem) abort without auto-correction.

[KO] 격자 자료구조, 위상, 검증.

See USER_GUIDE section 4 (mesh file) and 4.4 (mesh checks).
공개 문서 USER_GUIDE 4장·4.4절 참조.
코드는 격자를 만들지 않는다. 전량 외부 입력이다.
"""
from __future__ import annotations
import hashlib
import numpy as np
from . import elements as E


class MeshError(Exception):
    """격자 오류. 자동 교정 없이 중단한다 (CONTRIBUTING 원칙 1).

    Mesh error. Aborts without auto-correction (CONTRIBUTING, principle 1).
    """


class Mesh:
    """절점·요소·집합.

    nodes  (nn, 2) float64   (r, z) [m]
    elems  list[np.ndarray]  요소마다 길이가 다르다 (§5.2)
    emat   (ne,)  재료 이름
    qvol   (ne,)  체적 발열률 [W/m^3]   (§7)
    nsets  dict[str, np.ndarray]  절점 집합 (§8.2)
    """

    def __init__(self, nodes, elems, emat, qvol=None, nsets=None):
        self.nodes = np.ascontiguousarray(nodes, dtype=float)
        if self.nodes.ndim != 2 or self.nodes.shape[1] != 2:
            raise MeshError("nodes 는 (nn, 2) 이어야 한다")
        if np.any(self.nodes[:, 0] < 0.0):
            bad = np.where(self.nodes[:, 0] < 0.0)[0]
            raise MeshError("음의 반경 절점 %d 개, 예: %s" % (bad.size, bad[:5]))
        self.elems = [np.asarray(c, dtype=np.int64) for c in elems]
        self.emat = np.asarray(emat, dtype=object)
        self.ne = len(self.elems)
        self.nn = len(self.nodes)
        self.qvol = np.zeros(self.ne) if qvol is None else np.asarray(qvol, float)
        self.nsets = {k: np.asarray(v, dtype=np.int64) for k, v in (nsets or {}).items()}

        self.etype = np.empty(self.ne, dtype=np.int64)
        for e, c in enumerate(self.elems):
            n = len(c)
            if n not in E.SUPPORTED:
                raise MeshError("요소 %d 의 절점 수 %d 는 지원하지 않는다 (지원: %s)"
                                % (e, n, list(E.SUPPORTED)))
            if len(set(c.tolist())) != n:
                raise MeshError("요소 %d 에 중복 절점이 있다: %s" % (e, c.tolist()))
            if c.min() < 0 or c.max() >= self.nn:
                raise MeshError("요소 %d 의 절점 번호가 범위를 벗어난다" % e)
            self.etype[e] = n
        self._edges = None

    # ------------------------------------------------------------------
    # 지문 (§4.2)
    # ------------------------------------------------------------------
    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self.nodes.tobytes())
        for c in self.elems:
            h.update(c.astype(np.int64).tobytes())
        for m in self.emat:
            h.update(str(m).encode("utf-8"))
        h.update(self.qvol.tobytes())
        for k in sorted(self.nsets):
            h.update(k.encode("utf-8"))
            h.update(np.sort(self.nsets[k]).astype(np.int64).tobytes())
        return h.hexdigest()[:32]

    # ------------------------------------------------------------------
    # 위상 — 변 공유 (§9.2 G4, §10.2)
    # ------------------------------------------------------------------
    def edges(self):
        """변 사전.  key = 정렬된 코너 절점 쌍 -> [(elem, local_edge), ...]"""
        if self._edges is not None:
            return self._edges
        d = {}
        for e, c in enumerate(self.elems):
            et = self.etype[e]
            for le in range(E.N_EDGE[et]):
                i1, i2, _ = E.edge_nodes(et, le)
                key = (min(c[i1], c[i2]), max(c[i1], c[i2]))
                d.setdefault(key, []).append((e, le))
        for key, lst in d.items():
            if len(lst) > 2:
                raise MeshError("변 %s 를 요소 %d 개가 공유한다 (최대 2)"
                                % (str(key), len(lst)))
        self._edges = d
        return d

    def boundary_edges(self):
        """외곽 변 — 한 요소만 소유하는 변. [(elem, local_edge), ...]"""
        return [lst[0] for lst in self.edges().values() if len(lst) == 1]

    def edge_node_ids(self, e: int, le: int):
        """변의 전역 절점 번호 (코너1, 코너2, 중간절점 or None)."""
        c = self.elems[e]
        i1, i2, im = E.edge_nodes(self.etype[e], le)
        return int(c[i1]), int(c[i2]), (int(c[im]) if im is not None else None)

    # ------------------------------------------------------------------
    # 기하
    # ------------------------------------------------------------------
    def elem_geom(self, e: int, bump: int = 0):
        """적분점에서의 (N, dNdr, dNdz, detJ, r, w).  shape (nn, npt) / (npt,)"""
        et = self.etype[e]
        X = self.nodes[self.elems[e]]           # (nn, 2)
        xi, eta, w = E.quadrature(et, bump)
        N, dNx, dNe = E.shape(et, xi, eta)      # (nn, npt)
        J11 = dNx.T @ X[:, 0]                   # dr/dxi   (npt,)
        J12 = dNx.T @ X[:, 1]                   # dz/dxi
        J21 = dNe.T @ X[:, 0]                   # dr/deta
        J22 = dNe.T @ X[:, 1]                   # dz/deta
        det = J11 * J22 - J12 * J21
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = 1.0 / det
        # [dN/dr; dN/dz] = (1/det) [[J22, -J12], [-J21, J11]] [dN/dxi; dN/deta]
        # ※ J12 와 J21 을 바꿔 쓰면, 축에 정렬된 격자(J12 = J21 = 0)에서는
        #    오류가 상쇄되어 드러나지 않는다. 비직교 요소에서만 나타난다.
        dNdr = (J22 * inv) * dNx + (-J12 * inv) * dNe
        dNdz = (-J21 * inv) * dNx + (J11 * inv) * dNe
        r = N.T @ X[:, 0]
        return N, dNdr, dNdz, det, r, w

    def elem_volume(self, e: int, bump: int = 0) -> float:
        """축대칭 부피  ∫ 2*pi*r dA."""
        _, _, _, det, r, w = self.elem_geom(e, bump)
        return float(np.sum(2.0 * np.pi * r * det * w))

    def total_volume(self, bump: int = 0) -> float:
        return float(sum(self.elem_volume(e, bump) for e in range(self.ne)))

    def boundary_volume(self, bump: int = 2) -> float:
        """발산정리로 구한 부피 (§9.2 G4).

        V = ∮ pi*r^2 dz,  외곽을 반시계로 순회.
        요소 국소 변 순서가 반시계이므로, 각 외곽 변을 그 방향대로 적분하면 된다.
        """
        u, wq = E.edge_quadrature(2 + bump)
        tot = 0.0
        for e, le in self.boundary_edges():
            et = self.etype[e]
            idx, Nb, dNb = E.edge_shape(et, le, u)
            X = self.nodes[self.elems[e]][idx]          # (m, 2)
            r = Nb.T @ X[:, 0]
            dz = dNb.T @ X[:, 1]
            tot += float(np.sum(np.pi * r * r * dz * wq))
        return tot

    # ------------------------------------------------------------------
    # 검증 (§9.2)
    # ------------------------------------------------------------------
    def check(self, bump: int = 0, report: dict | None = None):
        rep = {} if report is None else report
        # --- G1  야코비안 양수 -----------------------------------------
        bad = []
        dmin = np.inf
        for e in range(self.ne):
            _, _, _, det, _, _ = self.elem_geom(e, bump)
            dmin = min(dmin, float(det.min()))
            if np.any(det <= 0.0):
                g = int(np.argmin(det))
                bad.append((e, g, float(det[g])))
        rep["G1_det_min"] = dmin
        rep["G1_bad"] = bad
        if bad:
            raise MeshError(
                "G1 위반 — 야코비안이 양수가 아닌 요소 %d 개. 예: %s"
                % (len(bad), bad[:5]))

        # --- G2  면적 대조 ---------------------------------------------
        # 코너 다각형 면적(부호)  vs  형상함수 Gauss 적분 면적
        worst_ratio, worst_e = 0.0, -1
        neg = []
        for e in range(self.ne):
            et = self.etype[e]
            C = self.nodes[self.elems[e][:E.N_CORNER[et]]]
            a_poly = 0.5 * float(np.sum(C[:, 0] * np.roll(C[:, 1], -1)
                                        - np.roll(C[:, 0], -1) * C[:, 1]))
            _, _, _, det, _, w = self.elem_geom(e, bump)
            a_gauss = float(np.sum(det * w))
            if a_poly <= 0.0:
                neg.append((e, a_poly))
            d = abs(a_gauss - a_poly) / max(abs(a_gauss), abs(a_poly), 1e-300)
            if d > worst_ratio:
                worst_ratio, worst_e = d, e
        rep["G2_worst_rel_diff"] = worst_ratio
        rep["G2_worst_elem"] = worst_e
        rep["G2_negative"] = neg
        if neg:
            raise MeshError("G2 위반 — 코너 서명 면적이 양수가 아닌 요소 %d 개. 예: %s"
                            % (len(neg), neg[:5]))

        # --- G4  발산정리 -----------------------------------------------
        v_elem = self.total_volume(bump)
        v_bnd = self.boundary_volume()
        scale = max(abs(v_elem), abs(v_bnd), 1e-300)
        rel = abs(v_elem - v_bnd) / scale
        # 허용오차: 고정 상수가 아니라 항의 개수에서 유도한다 (미결 M-3 확정)
        tol = 64.0 * self.ne * np.finfo(float).eps
        rep["G4_volume_element"] = v_elem
        rep["G4_volume_boundary"] = v_bnd
        rep["G4_rel_diff"] = rel
        rep["G4_tol"] = tol
        if rel > tol:
            raise MeshError("G4 위반 — 부피 상대차 %.3e > 허용 %.3e "
                            "(요소적분 %.12e, 표면적분 %.12e)"
                            % (rel, tol, v_elem, v_bnd))

        # --- 절점 중복 (§9.3, 미결 M-4 확정: 완전 동일 좌표만 판정) -------
        _, inv, cnt = np.unique(self.nodes, axis=0, return_inverse=True,
                                return_counts=True)
        dup = int(np.sum(cnt - 1))
        rep["duplicate_nodes"] = dup
        if dup:
            rep["duplicate_examples"] = [int(i) for i in
                                         np.where(cnt[inv] > 1)[0][:10]]
        return rep


# ----------------------------------------------------------------------
# 파일 입출력 (§5, 미결 M-10 확정: NPZ 기본)
# ----------------------------------------------------------------------
def save_npz(path, mesh: Mesh):
    flat = np.concatenate([c for c in mesh.elems]) if mesh.ne else np.zeros(0, np.int64)
    off = np.cumsum([0] + [len(c) for c in mesh.elems]).astype(np.int64)
    d = dict(schema_version=np.array("1.0"),
             nodes=mesh.nodes, elem_flat=flat, elem_offset=off,
             elem_material=mesh.emat.astype("U32"), elem_qvol=mesh.qvol)
    for k, v in mesh.nsets.items():
        d["nset__" + k] = np.asarray(v, dtype=np.int64)
    np.savez_compressed(path, **d)


def load_npz(path, length_unit: float = 1.0) -> Mesh:
    z = np.load(path, allow_pickle=False)
    off = z["elem_offset"]
    flat = z["elem_flat"]
    elems = [flat[off[i]:off[i + 1]] for i in range(len(off) - 1)]
    nsets = {k[len("nset__"):]: z[k] for k in z.files if k.startswith("nset__")}
    return Mesh(z["nodes"] * float(length_unit), elems, z["elem_material"],
                z["elem_qvol"], nsets)
