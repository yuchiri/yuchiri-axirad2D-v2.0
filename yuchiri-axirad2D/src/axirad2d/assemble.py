# -*- coding: utf-8 -*-
"""[EN] Boundary conditions and global assembly of residual and Jacobian.

Specification sections 3.3, 8, 11, 12.3.  Sign convention: heat flux into the
domain is positive.

[KO] 경계조건 처리와 전역 조립.

See USER_GUIDE sections 5 to 7 (materials, boundary conditions, sources).
공개 문서 USER_GUIDE 5~7장 참조.
부호 규약 — 영역 안으로 들어오는 열유속이 양(+) (§8.1).
"""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp
from . import elements as E
from .materials import SIGMA, check_k_positive
from .mesh import Mesh


class BCError(Exception):
    pass


# ----------------------------------------------------------------------
class Faces:
    """절점 집합에서 유도한 면적분 대상 변 (§8.3)."""

    def __init__(self, name, items, area, unused_nodes):
        self.name = name
        self.items = items                 # [(elem, local_edge), ...]
        self.area = area                   # [m^2]
        self.unused_nodes = unused_nodes


def faces_from_nset(mesh: Mesh, name: str, bump: int = 1) -> Faces:
    """외곽 변 중 모든 절점이 집합에 속하는 변 (§8.3)."""
    if name not in mesh.nsets:
        raise BCError("절점 집합 '%s' 이 격자에 없다" % name)
    S = set(int(i) for i in mesh.nsets[name])
    items, used = [], set()
    for e, le in mesh.boundary_edges():
        a, b, m = mesh.edge_node_ids(e, le)
        need = [a, b] + ([m] if m is not None else [])
        if all(n in S for n in need):
            items.append((e, le))
            used.update(need)
    area = sum(_edge_area(mesh, e, le, bump) for e, le in items)
    return Faces(name, items, area, sorted(S - used))


def _edge_area(mesh: Mesh, e: int, le: int, bump: int = 1) -> float:
    u, w = E.edge_quadrature(2 + bump)
    idx, Nb, dNb = E.edge_shape(mesh.etype[e], le, u)
    X = mesh.nodes[mesh.elems[e]][idx]
    r = Nb.T @ X[:, 0]
    dr = dNb.T @ X[:, 0]
    dz = dNb.T @ X[:, 1]
    ds = np.hypot(dr, dz)
    return float(np.sum(2.0 * np.pi * r * ds * w))


# ----------------------------------------------------------------------
class Assembler:
    def __init__(self, mesh: Mesh, materials: dict, bcs: list, segs, B,
                 bump: int = 0, blood: dict | None = None):
        # blood = {"rho_cb": [J/(m^3 K)], "T_arterial": [K]}
        # 관류를 쓰는 재료가 하나라도 있는데 혈액 정보가 없으면 중단한다.
        # 조용히 0 으로 두면 열싱크가 통째로 사라진 채 계산이 진행된다.
        self.blood = blood
        need = [m.name for m in materials.values() if getattr(m, "perfusion", 0.0) > 0.0]
        if need and not blood:
            raise BCError(
                "관류율이 0 이 아닌 재료 %s 가 있으나 혈액 물성(blood)이 주어지지 "
                "않았다. rho_cb 와 T_arterial 이 필요하다." % need)
        self.mesh = mesh
        self.mat = materials
        self.bcs = bcs
        self.S = segs
        self.bump = bump
        self.faces = {}
        for bc in bcs:
            if bc["type"] != "dirichlet":
                self.faces[bc["nset"]] = faces_from_nset(mesh, bc["nset"])
        # Dirichlet 절점
        self.dir_nodes, self.dir_vals = [], []
        for bc in bcs:
            if bc["type"] == "dirichlet":
                nl = mesh.nsets[bc["nset"]]
                self.dir_nodes.append(np.asarray(nl, dtype=np.int64))
                self.dir_vals.append(np.full(len(nl), float(bc["T"])))
        if self.dir_nodes:
            self.dir_nodes = np.concatenate(self.dir_nodes)
            self.dir_vals = np.concatenate(self.dir_vals)
        else:
            self.dir_nodes = np.zeros(0, dtype=np.int64)
            self.dir_vals = np.zeros(0)
        self.free_mask = np.ones(mesh.nn, dtype=bool)
        self.free_mask[self.dir_nodes] = False
        # 복사 결합 행렬  Q_s = sum_b M[s,b] T_b^4 - D_s T_s^4   (§12.3)
        if segs is not None and len(segs):
            w = SIGMA * segs.area * segs.eps
            self.Mrad = (B * w[:, None]).T.copy()     # M[s,b] = sigma A_b eps_b B_bs
            self.Drad = w.copy()
        else:
            self.Mrad = None
            self.Drad = None

    # ------------------------------------------------------------------
    def residual_jacobian(self, T):
        mesh, mat = self.mesh, self.mat
        R = np.zeros(mesh.nn)
        rows, cols, vals = [], [], []
        P_source = 0.0
        P_met = 0.0            # 대사 발열 총합 [W]
        P_perf = 0.0           # 관류가 조직에 넣어 준 순 열량 [W] (음수면 냉각)

        # --- 전도 + 열원 ------------------------------------------------
        for e in range(mesh.ne):
            c = mesh.elems[e]
            N, dNr, dNz, det, r, w = mesh.elem_geom(e, self.bump)
            Te = T[c]
            Tg = N.T @ Te
            m = mat[str(mesh.emat[e])]
            kg = np.atleast_1d(m.k(Tg))
            check_k_positive(m.name, kg)
            dkg = np.atleast_1d(m.k.d(Tg))
            jac = 2.0 * np.pi * r * det * w
            gr = dNr.T @ Te
            gz = dNz.T @ Te
            R[c] += (dNr * (kg * gr * jac)).sum(axis=1) + (dNz * (kg * gz * jac)).sum(axis=1)
            q = mesh.qvol[e]
            if q:
                R[c] -= (N * (q * jac)).sum(axis=1)
                P_source += float(np.sum(q * jac))
            # --- 대사 발열 (§Pennes) ------------------------------------
            if m.q_met:
                R[c] -= (N * (m.q_met * jac)).sum(axis=1)
                P_met += float(np.sum(m.q_met * jac))
            Ke = (dNr * (kg * jac)) @ dNr.T + (dNz * (kg * jac)) @ dNz.T
            Ke += (dNr * (dkg * gr * jac) + dNz * (dkg * gz * jac)) @ N.T
            # --- 관류 (Pennes 열싱크) -----------------------------------
            #   기여:  - w_b rho_b c_b (T_a - T)  를 우변에서 뺀다
            #   야코비안:  + w_b rho_b c_b  (양의 정부호 -> 안정화)
            #   perfusion = 0 이면 이 블록을 건너뛰므로, 관류 없는 문제의
            #   결과는 이 기능 추가 전과 비트 단위로 동일하다.
            if m.perfusion:
                wrc = m.perfusion * self.blood["rho_cb"]
                Ta = self.blood["T_arterial"]
                R[c] -= (N * (wrc * (Ta - Tg) * jac)).sum(axis=1)
                P_perf += float(np.sum(wrc * (Ta - Tg) * jac))
                Ke = Ke + (N * (wrc * jac)) @ N.T
            rows.append(np.repeat(c, len(c)))
            cols.append(np.tile(c, len(c)))
            vals.append(Ke.ravel())

        # --- 경계조건 (면적분) ------------------------------------------
        P_bnd = {}
        for bc in self.bcs:
            t = bc["type"]
            if t in ("dirichlet", "adiabatic"):
                continue
            F = self.faces[bc["nset"]]
            acc = 0.0
            for e, le in F.items:
                c = mesh.elems[e]
                u, wq = E.edge_quadrature(2 + self.bump + 1)
                idx, Nb, dNb = E.edge_shape(mesh.etype[e], le, u)
                g = c[idx]
                X = mesh.nodes[g]
                r = Nb.T @ X[:, 0]
                ds = np.hypot(dNb.T @ X[:, 0], dNb.T @ X[:, 1])
                jac = 2.0 * np.pi * r * ds * wq
                Tg = Nb.T @ T[g]
                if t == "flux":
                    qin = np.full_like(Tg, float(bc["q"]))
                    dq = np.zeros_like(Tg)
                elif t == "convection":
                    h, Tinf = float(bc["h"]), float(bc["T_inf"])
                    qin = h * (Tinf - Tg)
                    dq = -h * np.ones_like(Tg)
                elif t == "env_radiation":
                    eps, Tenv = float(bc["emissivity"]), float(bc["T_env"])
                    qin = eps * SIGMA * (Tenv ** 4 - Tg ** 4)
                    dq = -4.0 * eps * SIGMA * Tg ** 3
                else:
                    raise BCError("알 수 없는 경계조건 종류 '%s'" % t)
                R[g] -= (Nb * (qin * jac)).sum(axis=1)
                acc += float(np.sum(qin * jac))
                Ke = -(Nb * (dq * jac)) @ Nb.T
                rows.append(np.repeat(g, len(g)))
                cols.append(np.tile(g, len(g)))
                vals.append(Ke.ravel())
            P_bnd[bc["nset"] + ":" + t] = acc

        # --- enclosure 복사 (§12.3 완전 결합) ----------------------------
        P_rad = 0.0
        if self.Mrad is not None:
            S = self.S
            Ts = 0.5 * (T[S.n1] + T[S.n2])
            T4 = Ts ** 4
            Q = self.Mrad @ T4 - self.Drad * T4          # (ns,)
            P_rad = float(Q.sum())
            np.add.at(R, S.n1, -0.5 * Q)
            np.add.at(R, S.n2, -0.5 * Q)
            # dQ_s/dT_b = M[s,b] 4 T_b^3 ;  dQ_s/dT_s -= D_s 4 T_s^3
            dT4 = 4.0 * Ts ** 3
            Jrad = self.Mrad * dT4[None, :]
            Jrad[np.arange(len(S)), np.arange(len(S))] -= self.Drad * dT4
            # 절점 사상 0.5 (양쪽)
            blk = -0.25 * Jrad
            for na in (S.n1, S.n2):
                for nb in (S.n1, S.n2):
                    rows.append(np.repeat(na, len(S)))
                    cols.append(np.tile(nb, len(S)))
                    vals.append(blk.ravel())

        J = sp.coo_matrix((np.concatenate(vals),
                           (np.concatenate(rows), np.concatenate(cols))),
                          shape=(mesh.nn, mesh.nn)).tocsr()
        # 에너지 수지의 완결성 — 잔차 항등식 sum_i R_i = -(모든 열원) 이
        # 성립하려면 관류·대사도 항목으로 남아야 한다.
        power = dict(source=P_source, radiation_net=P_rad,
                     metabolic=P_met, perfusion_net=P_perf, **P_bnd)
        return R, J, power

    # ------------------------------------------------------------------
    def apply_dirichlet(self, R, J, T):
        Rd = R.copy()
        Rd[self.dir_nodes] = T[self.dir_nodes] - self.dir_vals
        Jd = J.tolil(copy=True)
        for n in self.dir_nodes:
            Jd.rows[n] = [int(n)]
            Jd.data[n] = [1.0]
        return Rd, Jd.tocsr()
