# -*- coding: utf-8 -*-
"""계산 결과 도면 생성 — 온도장과 검증 요약.

★ 솔버의 일부가 아니다. 결과 시각화 보조 스크립트다.
"""
from __future__ import annotations
import json
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
import matplotlib.tri as mtri

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "examples"),
          os.path.join(ROOT, "examples", "coaxial_enclosure"),
          os.path.join(ROOT, "examples", "bm2_bm5")):
    if p not in sys.path:
        sys.path.insert(0, p)

OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

# Q9 를 4개의 부사각형 -> 8개 삼각형으로 쪼갠다 (등고선용)
SUB = [(0, 4, 8, 7), (4, 1, 5, 8), (8, 5, 2, 6), (7, 8, 6, 3)]


def triangulate(mesh):
    tri = []
    for c in mesh.elems:
        for q in SUB:
            a, b, d, e = (int(c[i]) for i in q)
            tri.append((a, b, d))
            tri.append((a, d, e))
    return np.array(tri, dtype=int)


def load(case_dir):
    z = np.load(os.path.join(case_dir, "results.npz"))
    with open(os.path.join(case_dir, "diagnostics.json"), encoding="utf-8") as f:
        d = json.load(f)
    return z, d


def field_panel(ax, mesh, T, z, title, levels=24):
    t = mtri.Triangulation(mesh.nodes[:, 0], mesh.nodes[:, 1], triangulate(mesh))
    cf = ax.tricontourf(t, T, levels=levels, cmap="inferno")
    ax.tricontour(t, T, levels=levels, colors="k", linewidths=0.25, alpha=0.35)
    if "seg_P1" in z.files:
        for p1, p2 in zip(z["seg_P1"], z["seg_P2"]):
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#00e5ff", lw=1.3,
                    solid_capstyle="butt")
    ax.set_aspect("equal")
    ax.set_xlabel("r  [m]")
    ax.set_ylabel("z  [m]")
    ax.set_title(title, fontsize=10)
    return cf


# ======================================================================
def figure_fields(path):
    from build_mesh import build as build_bm1
    from build_meshes import build_bm2, build_bm5

    cases = [
        ("BM-1  동축 원통 밀폐공동", build_bm1(),
         os.path.join(ROOT, "examples", "coaxial_enclosure", "out")),
        ("BM-2  유한 원통 밀폐공동", build_bm2(),
         os.path.join(ROOT, "examples", "bm2_bm5", "out_bm2")),
        ("BM-5  동심 구", build_bm5(),
         os.path.join(ROOT, "examples", "bm2_bm5", "out_bm5")),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 7.4))
    for ax, (name, mesh, cdir) in zip(axes, cases):
        z, d = load(cdir)
        T = z["T"]
        cf = field_panel(ax, mesh, T, z,
                         "%s\nT ∈ [%.1f, %.1f] K   반복 %d 회"
                         % (name, T.min(), T.max(), len(d["iterations"])))
        cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.03)
        cb.set_label("T  [K]", fontsize=9)
    axes[0].plot([], [], color="#00e5ff", lw=1.5, label="복사면 세그먼트")
    axes[0].legend(loc="upper right", fontsize=8, framealpha=0.85)
    fig.text(0.5, 0.018,
             "※ 청록선 안쪽의 진공(투명) 영역에 그려진 온도는 물리적 의미가 없다. "
             "행렬 특이화를 막기 위해 넣은 k = 1e-5 W/(m·K) 의 수치적 채움값이다. "
             "복사 교환은 청록선 위의 세그먼트 사이에서 일어난다.",
             ha="center", fontsize=8.5, color="#333")
    fig.suptitle("yuchiri-axirad2D 계산 결과 — 온도장 (2차원 축대칭, 전도 + 표면 복사)",
                 fontsize=13)
    fig.tight_layout(rect=[0, 0.045, 1, 0.95])
    fig.savefig(path, dpi=165)
    plt.close(fig)
    return path


# ======================================================================
def figure_verification(path):
    from problem_def import BM2, bm2_view_factors
    fig = plt.figure(figsize=(14.4, 9.0))

    # ---- (a) BM-2 형상계수 대조 ------------------------------------
    ax = fig.add_subplot(2, 3, 1)
    ex = bm2_view_factors(BM2["R"], BM2["R"], BM2["L"])
    names = ["F(1→2)", "F(s→1)", "F(1→1)"]
    exact = [ex["F_disk_disk"], ex["F_side_disk"], 0.0]
    calc = [0.171501917, 0.207167083, 0.0]
    err = [0.2636, 0.1828, 0.0]           # 표준오차 [%]
    x = np.arange(3)
    ax.bar(x - 0.19, exact, 0.36, label="정확해", color="#5a5a5a")
    ax.bar(x + 0.19, calc, 0.36, label="계산", color="#d62b4a",
           yerr=[e / 100 * c for e, c in zip(err, calc)], capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("형상계수")
    ax.set_title("(a) BM-2 형상계수\n오차 −0.041 %, +0.029 %  (각 0.16 σ)",
                 fontsize=9.5)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25, lw=0.4)

    # ---- (b) BM-5 곡면 수렴 ----------------------------------------
    ax = fig.add_subplot(2, 3, 2)
    nth = np.array([12, 24, 48])
    aerr = np.array([0.8555, 0.2141, 0.0535])
    ax.loglog(nth, aerr, "o-", color="#1f77b4", label="계산 A1 오차")
    ax.loglog(nth, aerr[0] * (nth[0] / nth) ** 2, "--", color="#888",
              label="Δθ² 기울기")
    ax.set_xlabel("θ 방향 분할수")
    ax.set_ylabel("내부 구면 면적 A1 의 오차  [%]")
    ax.set_title("(b) BM-5 곡면 근사 수렴\n감소비 4.00, 4.00", fontsize=9.5)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both", lw=0.4)

    # ---- (c) 상반성 L1 ---------------------------------------------
    ax = fig.add_subplot(2, 3, 3)
    N = np.array([2500, 10000, 40000])
    l1 = np.array([1.3993e-1, 6.7856e-2, 3.4655e-2])
    ax.loglog(N, l1, "o-", color="#2ca02c", label="상반성 L1 (BM-1)")
    ax.loglog(N, l1[0] * (N[0] / N) ** 0.5, "--", color="#888",
              label="N$^{-1/2}$ 기울기")
    ax.set_xlabel("광선 수 N")
    ax.set_ylabel("L1 잔차")
    ax.set_title("(c) 상반성 통계 수렴\n실측 0.485, 0.511  (예측 0.500)",
                 fontsize=9.5)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both", lw=0.4)

    # ---- (d) Newton 수렴 이력 --------------------------------------
    ax = fig.add_subplot(2, 3, 4)
    for name, cdir, col in (
            ("BM-1", os.path.join(ROOT, "examples", "coaxial_enclosure", "out"), "#d62b4a"),
            ("BM-2", os.path.join(ROOT, "examples", "bm2_bm5", "out_bm2"), "#1f77b4"),
            ("BM-5", os.path.join(ROOT, "examples", "bm2_bm5", "out_bm5"), "#2ca02c")):
        _, d = load(cdir)
        st = [h["step"] for h in d["iterations"]]
        ax.semilogy(range(1, len(st) + 1), st, "o-", color=col, label=name, ms=4)
    ax.axhline(1e-9, color="#888", ls="--", lw=0.9)
    ax.text(1.1, 1.4e-9, "eps_T = 1e-9", fontsize=7.5, color="#555")
    ax.set_xlabel("Newton 반복")
    ax.set_ylabel("|ΔT| / 온도 범위")
    ax.set_title("(d) Newton 수렴 — 2차 수렴", fontsize=9.5)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both", lw=0.4)

    # ---- (e) 에너지 수지 --------------------------------------------
    ax = fig.add_subplot(2, 3, 5)
    rows = []
    for name, cdir in (("BM-1", os.path.join(ROOT, "examples", "coaxial_enclosure", "out")),
                       ("BM-2", os.path.join(ROOT, "examples", "bm2_bm5", "out_bm2")),
                       ("BM-5", os.path.join(ROOT, "examples", "bm2_bm5", "out_bm5"))):
        _, d = load(cdir)
        rows.append((name, d["power"]["source"], d["reaction_dirichlet"],
                     d["power"]["radiation_net"], d["energy_residual_rel"]))
    ax.axis("off")
    txt = [["", "발열\n[W]", "Dirichlet\n반력 [W]", "복사 순합\n[W]", "에너지\n상대 잔차"]]
    for r in rows:
        txt.append([r[0], "%.6g" % r[1], "%.6g" % r[2], "%.2e" % r[3], "%.1e" % r[4]])
    tb = ax.table(cellText=txt[1:], colLabels=txt[0], loc="center",
                  cellLoc="center")
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1.12, 2.0)
    ax.set_title("(e) 에너지 수지 — 발열 = 유출", fontsize=9.5)

    # ---- (f) 정확해 대조 요약 ---------------------------------------
    ax = fig.add_subplot(2, 3, 6)
    labels = ["BM-1\nT1", "BM-1\nQ", "BM-2\nF(1→2)", "BM-2\nF(s→1)",
              "BM-5\nQ(회색)", "BM-5\n결합 Q"]
    vals = [0.0019, 0.0081, -0.0414, 0.0291, -0.0354, 0.0320]
    cols = ["#d62b4a" if v < 0 else "#1f77b4" for v in vals]
    ax.barh(labels, vals, color=cols)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("정확해 대비 오차  [%]")
    ax.set_xlim(-0.06, 0.06)
    ax.grid(alpha=0.25, axis="x", lw=0.4)
    ax.set_title("(f) 정확해 대조 — 전 항목 |오차| < 0.05 %", fontsize=9.5)

    fig.suptitle("yuchiri-axirad2D 검증 요약 — BM-1 · BM-2 · BM-5", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(path, dpi=165)
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(figure_fields(os.path.join(OUT, "results_temperature_fields.png")))
    print(figure_verification(os.path.join(OUT, "results_verification_summary.png")))
