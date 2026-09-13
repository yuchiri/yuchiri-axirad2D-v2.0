# -*- coding: utf-8 -*-
"""Benchmark definition figure (BM-1, BM-2, BM-5) with bilingual labels.
벤치마크 정의 도면 (BM-1, BM-2, BM-5), 영·한 병기.

Not part of the solver. / 솔버의 일부가 아니다.
"""
from __future__ import annotations
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
def _use_cjk_font():
    """[EN] Pick a font that can draw Korean, wherever we are running.
    Falls back silently to the default font; the figure is still correct, only
    the Korean labels may show as boxes.
    [KO] 어디서 실행하든 한글을 그릴 수 있는 폰트를 고른다. 없으면 기본 폰트로
    조용히 물러난다. 도면은 그대로이고 한글 라벨만 네모로 보일 수 있다.
    """
    import os
    from matplotlib import font_manager, rcParams
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",   # Linux
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",               # macOS
        "/Library/Fonts/AppleGothic.ttf",                           # macOS
        "C:/Windows/Fonts/malgun.ttf",                              # Windows
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                rcParams["font.family"] = font_manager.FontProperties(
                    fname=p).get_name()
                rcParams["axes.unicode_minus"] = False
                return
            except Exception:
                pass
    for name in ("Noto Sans CJK JP", "Apple SD Gothic Neo", "AppleGothic",
                 "Malgun Gothic", "NanumGothic"):
        if any(f.name == name for f in font_manager.fontManager.ttflist):
            rcParams["font.family"] = name
            rcParams["axes.unicode_minus"] = False
            return
    rcParams["axes.unicode_minus"] = False

_use_cjk_font()
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "bm2_bm5"))
from problem_def import BM2, BM5                      # noqa: E402

SOLID = "#8a8a8a"
VAC = "#dceaf7"
HOT = "#e8a33d"


def draw(path):
    fig, ax = plt.subplots(1, 3, figsize=(16.2, 8.0))

    # ================= BM-1 =================
    a, zi0, zi1 = 0.05, 0.05, 0.15
    b, zc0, zc1 = 0.10, 0.02, 0.18
    c, zl, zh = 0.12, 0.00, 0.20
    A = ax[0]
    A.add_patch(Rectangle((0, zl), c, zh - zl, facecolor=SOLID, edgecolor="k", lw=1.1))
    A.add_patch(Rectangle((0, zc0), b, zc1 - zc0, facecolor=VAC, edgecolor="none"))
    A.add_patch(Rectangle((0, zi0), a, zi1 - zi0, facecolor=HOT, edgecolor="k", lw=1.0))
    A.plot([a, a], [zi0, zi1], color="#d62b4a", lw=3)
    A.plot([0, a], [zi0, zi0], color="#d62b4a", lw=3)
    A.plot([0, a], [zi1, zi1], color="#d62b4a", lw=3)
    A.plot([b, b], [zc0, zc1], color="#1f77b4", lw=3)
    A.plot([0, b], [zc0, zc0], color="#1f77b4", lw=3)
    A.plot([0, b], [zc1, zc1], color="#1f77b4", lw=3)
    A.text(0.012, 0.099, "inner body\n내부물체\nq = 200 W\ne1 = 0.8", fontsize=8.5)
    A.text(0.058, 0.165, "vacuum\n진공", fontsize=8.5)
    A.text(0.102, 0.100, "solid / 고체", fontsize=8, rotation=90, color="w")
    A.text(0.008, 0.208, "outer 3 faces Dirichlet 300 K\n외곽 3면 Dirichlet 300 K", fontsize=8)
    A.text(0.062, 0.036, "cavity wall 공동벽\ne2 = 1.0 (black 흑체)", fontsize=8, color="#1f77b4")
    A.set_xlim(-0.012, 0.145)
    A.set_ylim(-0.012, 0.238)
    A.set_title("BM-1  Coaxial cylindrical enclosure\n동축 원통 밀폐공동\n"
                "convex body fully enclosed → F(1→2)=1\n볼록체 완전 포위", fontsize=9.5)

    # ================= BM-2 =================
    R, L, t = BM2["R"], BM2["L"], BM2["T"]
    B = ax[1]
    B.add_patch(Rectangle((0, -t), R + t, L + 2 * t, facecolor=SOLID, edgecolor="k", lw=1.1))
    B.add_patch(Rectangle((0, -t), R + t, t, facecolor=HOT, edgecolor="k", lw=1.0))
    B.add_patch(Rectangle((0, 0), R, L, facecolor=VAC, edgecolor="none"))
    B.plot([0, R], [0, 0], color="#d62b4a", lw=3.2)
    B.plot([0, R], [L, L], color="#1f77b4", lw=3.2)
    B.plot([R, R], [0, L], color="#2ca02c", lw=3.2)
    B.annotate("", xy=(R, -0.032), xytext=(0, -0.032),
               arrowprops=dict(arrowstyle="<->", lw=1.0))
    B.text(R / 2, -0.040, "R = 0.05 m", ha="center", fontsize=8.5)
    B.annotate("", xy=(-0.021, L), xytext=(-0.021, 0),
               arrowprops=dict(arrowstyle="<->", lw=1.0))
    B.text(-0.026, L / 2, "L = 0.10 m", va="center", rotation=90, fontsize=8.5)
    B.text(0.008, 0.055, "vacuum\n진공", fontsize=8.5)
    B.text(0.012, 0.004, "disk 1 원판 1", color="#d62b4a", fontsize=8.5)
    B.text(0.012, L - 0.008, "disk 2 원판 2", color="#1f77b4", fontsize=8.5)
    B.text(0.026, 0.070, "side wall\n측벽 s", color="#2ca02c", fontsize=8.5)
    B.text(0.002, -0.014, "q = 150 W", fontsize=8)
    B.text(R + t + 0.003, L / 2, "Dirichlet\n300 K", fontsize=8, va="center")
    B.text(0.002, L + t * 0.35, "all faces black  e = 1.0\n전 면 흑체", fontsize=8)
    B.set_xlim(-0.033, 0.105)
    B.set_ylim(-0.050, 0.145)
    B.set_title("BM-2  Finite cylindrical enclosure\n유한 원통 밀폐공동\n"
                "black walls → B = F, non-trivial view factor\n전 면 흑체 → 비자명 형상계수", fontsize=9.5)

    # ================= BM-5 =================
    a0, aa, bb, cc = BM5["a0"], BM5["a"], BM5["b"], BM5["c"]
    C = ax[2]
    for rr, col in ((cc, SOLID), (bb, VAC), (aa, HOT)):
        C.add_patch(Wedge((0, 0), rr, -90, 90, facecolor=col, edgecolor="k", lw=1.0))
    C.add_patch(Wedge((0, 0), a0, -90, 90, facecolor="w", edgecolor="k", lw=1.0, ls="--"))
    th = np.linspace(-np.pi / 2, np.pi / 2, 240)
    C.plot(aa * np.cos(th), aa * np.sin(th), color="#d62b4a", lw=3.2)
    C.plot(bb * np.cos(th), bb * np.sin(th), color="#1f77b4", lw=3.2)
    for rr, lab in ((a0, "a0=0.02"), (aa, "a=0.04"), (bb, "b=0.08"), (cc, "c=0.10")):
        ang = np.deg2rad(-42)
        C.plot([0, rr * np.cos(ang)], [0, rr * np.sin(ang)], color="k", lw=0.6)
        C.text(rr * np.cos(ang) * 1.02, rr * np.sin(ang) * 1.02 - 0.005, lab, fontsize=7.5)
    C.text(0.010, 0.024, "solid 고체\nq = 300 W", fontsize=8)
    C.text(0.046, 0.052, "vacuum\n진공", fontsize=8.5)
    C.text(0.062, 0.112, "inner sphere 내부 구면  e1 = 0.8", color="#d62b4a", fontsize=8)
    C.text(0.062, 0.100, "cavity outer 공동 외면  e2 = 0.5", color="#1f77b4", fontsize=8)
    C.text(0.062, -0.110, "r = c : Dirichlet 300 K", fontsize=8)
    C.plot([0, 0], [-cc * 1.12, cc * 1.12], color="k", ls="-.", lw=1.0)
    C.text(-0.026, 0.0, "axis 회전축 (r = 0)", rotation=90, va="center", fontsize=7.5)
    C.set_xlim(-0.036, 0.160)
    C.set_ylim(-0.128, 0.128)
    C.set_title("BM-5  Concentric spheres\n동심 구\n"
                "uniform irradiation → gray formula exact\n조사량 균일 → 회색 정확해", fontsize=9.5)

    for A_ in ax:
        A_.set_aspect("equal")
        A_.set_xlabel("r  [m]")
        A_.set_ylabel("z  [m]")
        A_.grid(alpha=0.22, lw=0.4)
    fig.suptitle("yuchiri-axirad2D benchmark definitions / 벤치마크 정의   "
                 "(2D axisymmetric, surface-to-surface radiation)", fontsize=12.5)
    fig.text(0.5, 0.015,
             "Red 적색 = radiating surface 1 (inner)   Blue 청색 = radiating surface 2 (outer)   "
             "Green 녹색 = side wall 측벽   Orange 주황 = heat source 발열",
             ha="center", fontsize=8.5)
    fig.tight_layout(rect=[0, 0.035, 1, 0.94])
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(HERE), "figures",
                       "benchmark_definitions.png")
    print(draw(out))
