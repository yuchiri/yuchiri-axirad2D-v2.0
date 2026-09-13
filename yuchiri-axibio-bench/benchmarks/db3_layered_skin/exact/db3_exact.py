# -*- coding: utf-8 -*-
"""DB-3 exact solution / DB-3 정확해.

Layered steady Pennes bioheat with convective + radiative surface loss.
다층 정상 Pennes 생체열전달, 표면에서 대류 + 복사 손실.

WHY THIS IS AN EXACT SOLUTION / 왜 이것이 정확해인가
-----------------------------------------------------
In each layer with constant k_i, w_i, q_met,i the equation

    k_i T'' + w_i rho_b c_b (T_a - T) + q_met,i = 0

is linear with constant coefficients, so its general solution is known in
closed form.  Continuity of T and of k T' at the interfaces makes the whole
stack a LINEAR map from the surface state to the core state.  The only
nonlinearity in the problem is the radiative boundary condition, and it
involves ONE unknown scalar (the surface temperature).  So the exact solution
is: closed-form everywhere, plus a scalar Newton solve whose residual can be
driven to machine precision.

각 층에서 방정식이 상수계수 선형이므로 일반해가 닫힌 형태로 알려져 있다.
계면에서 T 와 k T' 의 연속을 요구하면 적층 전체가 '표면 상태 -> 심부 상태' 의
선형 사상이 된다.  문제의 유일한 비선형성은 복사 경계조건이며 미지수가 표면
온도 하나뿐이다.  따라서 정확해 = 닫힌 형태 + 스칼라 Newton 이고, 그 잔차를
기계 정밀도까지 낮출 수 있다.

Sign convention follows the solver: heat flux INTO the domain is positive.
부호 규약은 솔버를 따른다 — 영역 안으로 들어오는 열유속이 양(+).
"""
from __future__ import annotations
import numpy as np

SIGMA = 5.670374419e-08          # W/(m^2 K^4)


class Layer:
    """One tissue layer. / 조직 한 층.

    L      thickness [m]
    k      thermal conductivity [W/(m K)]
    w      blood perfusion rate omega_b [1/s]  (0 for avascular tissue)
    q_met  metabolic heat generation [W/m^3]
    """

    def __init__(self, name, L, k, w, q_met):
        self.name = name
        self.L = float(L)
        self.k = float(k)
        self.w = float(w)
        self.q_met = float(q_met)


class Stack:
    """Layers ordered from the CORE side (x = 0) to the SURFACE (x = L_tot).

    층은 심부(x = 0)에서 표면(x = L_tot) 순서로 준다.
    """

    def __init__(self, layers, rho_cb, T_a):
        self.layers = list(layers)
        self.rho_cb = float(rho_cb)          # blood volumetric heat capacity
        self.T_a = float(T_a)                # arterial temperature [K]
        self.x = np.concatenate([[0.0], np.cumsum([l.L for l in self.layers])])
        self.L_tot = float(self.x[-1])

    # ------------------------------------------------------------------
    def _layer_transfer(self, layer):
        """2x2 transfer matrix of one layer, plus its particular part.

        State vector  s = [ theta ; k dtheta/dx ]   with theta = T - T_a.
        Returns (M, p) such that   s(x_end) = M @ s(x_start) + p .

        상태벡터 s = [theta ; k dtheta/dx] 에 대해 s(끝) = M s(시작) + p.
        Using a flux-like second component makes M continuous across
        interfaces, because T and k dT/dx are exactly what must be continuous.
        두 번째 성분을 유속으로 잡으면 계면에서 M 이 그대로 이어진다.
        T 와 k dT/dx 가 바로 연속이어야 하는 양이기 때문이다.
        """
        L, k, w, qm = layer.L, layer.k, layer.w, layer.q_met
        if w > 0.0:
            kap = np.sqrt(w * self.rho_cb / k)
            c, s = np.cosh(kap * L), np.sinh(kap * L)
            M = np.array([[c,          s / (k * kap)],
                          [k * kap * s, c]])
            # particular solution: theta_p = q_met / (w rho_b c_b), constant
            tp = qm / (w * self.rho_cb)
            p = np.array([tp - (M[0, 0] * tp), -(M[1, 0] * tp)])
        else:
            # w = 0 :  k theta'' = -q_met
            M = np.array([[1.0, L / k],
                          [0.0, 1.0]])
            p = np.array([-qm * L * L / (2.0 * k), -qm * L])
        return M, p

    def _core_to_surface(self):
        """Compose all layers: s(surface) = M @ s(core) + p."""
        M = np.eye(2)
        p = np.zeros(2)
        for layer in self.layers:
            Mi, pi = self._layer_transfer(layer)
            M = Mi @ M
            p = Mi @ p + pi
        return M, p

    # ------------------------------------------------------------------
    def solve(self, T_core, h, T_inf, eps, T_env, tol=1e-13, itmax=100):
        """Exact solution. Returns a dict with the surface state and profile fn.

        Boundary conditions
            x = 0        T = T_core                                 (Dirichlet)
            x = L_tot    -k dT/dx = h (T_s - T_inf) + eps sigma (T_s^4 - T_env^4)

        [EN] The surface loses heat by convection and radiation and by nothing
        else.  There is NO evaporative term: insensible perspiration and sweat
        are mass transfer, which is outside a heat-transfer benchmark.  A real
        skin balance carries that extra output, which is one reason the surface
        temperature computed here runs warmer than a measured one.
        [KO] 표면은 대류와 복사로만 열을 잃는다.  증발 항이 **없다**.  무감성
        발한과 땀은 물질전달이며 열전달 벤치마크의 범위 밖이다.  실제 피부의
        수지에는 그 출력 항이 더 있고, 여기서 계산된 표면 온도가 실측보다 따뜻하게
        나오는 이유 중 하나가 그것이다.

        The right-hand side is the flux LEAVING the body, so with the solver's
        inward-positive convention the surface flux is its negative.
        우변은 몸에서 나가는 유속이므로, 안쪽이 양인 규약에서는 그 음수다.
        """
        M, p = self._core_to_surface()
        th_core = T_core - self.T_a

        # unknown: q_core = k dtheta/dx at x = 0.
        # surface state is affine in it:
        #   theta_s = M00 th_core + M01 q_core + p0
        #   q_s     = M10 th_core + M11 q_core + p1
        a0, b0 = M[0, 0] * th_core + p[0], M[0, 1]
        a1, b1 = M[1, 0] * th_core + p[1], M[1, 1]

        def residual(q_core):
            th_s = a0 + b0 * q_core
            q_s = a1 + b1 * q_core                 # = k dtheta/dx at surface
            T_s = th_s + self.T_a
            # k dT/dx at the surface equals minus the outgoing flux
            out = h * (T_s - T_inf) + eps * SIGMA * (T_s ** 4 - T_env ** 4)
            return q_s + out, T_s

        # Newton on the single scalar q_core
        q = 0.0
        for _ in range(itmax):
            f, T_s = residual(q)
            # df/dq = b1 + [h + 4 eps sigma T_s^3] * b0
            df = b1 + (h + 4.0 * eps * SIGMA * T_s ** 3) * b0
            dq = -f / df
            q += dq
            if abs(dq) < tol * max(1.0, abs(q)):
                break
        else:
            raise RuntimeError("DB-3 참조해 Newton 이 수렴하지 않았다")

        f, T_s = residual(q)
        return dict(q_core=q, T_surface=T_s, residual=f,
                    T_of_x=self._profile(th_core, q))

    # ------------------------------------------------------------------
    def _profile(self, th_core, q_core):
        """Return T(x) as a callable, exact within each layer."""
        states = [np.array([th_core, q_core])]
        for layer in self.layers:
            Mi, pi = self._layer_transfer(layer)
            states.append(Mi @ states[-1] + pi)

        def T_of_x(x):
            x = np.atleast_1d(np.asarray(x, dtype=float))
            out = np.empty_like(x)
            for j, layer in enumerate(self.layers):
                x0, x1 = self.x[j], self.x[j + 1]
                m = (x >= x0 - 1e-12) & (x <= x1 + 1e-12)
                if not np.any(m):
                    continue
                xi = x[m] - x0
                th0, q0 = states[j]
                k, w, qm = layer.k, layer.w, layer.q_met
                if w > 0.0:
                    kap = np.sqrt(w * self.rho_cb / k)
                    tp = qm / (w * self.rho_cb)
                    A = th0 - tp
                    B = q0 / (k * kap)
                    out[m] = self.T_a + tp + A * np.cosh(kap * xi) \
                        + B * np.sinh(kap * xi)
                else:
                    out[m] = self.T_a + th0 + q0 * xi / k - qm * xi * xi / (2 * k)
            return out
        return T_of_x


# ----------------------------------------------------------------------
def total_surface_loss(T_s, h, T_inf, eps, T_env):
    """Outgoing surface heat flux [W/m^2]. / 표면에서 나가는 열유속."""
    return h * (T_s - T_inf) + eps * SIGMA * (T_s ** 4 - T_env ** 4)
