# -*- coding: utf-8 -*-
"""Figure: which claims the coefficients support. / 계수가 뒷받침하는 주장."""
import numpy as np, matplotlib
matplotlib.use("Agg")
def _font():
    import os
    from matplotlib import font_manager, rcParams
    for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
              "/System/Library/Fonts/AppleSDGothicNeo.ttc",
              "/Library/Fonts/AppleGothic.ttf","C:/Windows/Fonts/malgun.ttf"):
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                rcParams["font.family"]=font_manager.FontProperties(fname=p).get_name()
                rcParams["axes.unicode_minus"]=False; return
            except Exception: pass
    rcParams["axes.unicode_minus"]=False
_font()
import matplotlib.pyplot as plt
SIG=5.670374419e-08; Tenv=297.15
fig,ax=plt.subplots(1,3,figsize=(15.0,5.4))

# (a) 비 vs h, 여러 T_s
h=np.linspace(2.5,8.0,300)
for Tc,c in ((32,"#3b7dd8"),(34,"#2ca02c"),(36.3,"#d62b4a")):
    Ts=Tc+273.15
    ax[0].plot(h,0.98*SIG*(Ts**4-Tenv**4)/(h*(Ts-Tenv)),lw=2.2,color=c,
               label="$T_s$ = %.1f °C"%Tc)
ax[0].axhline(1.0,color="k",ls="--",lw=1.2)
ax[0].axvspan(3.1,5.1,color="#ffd9a0",alpha=0.5,label="전신 문헌 범위 3.1–5.1")
ax[0].axvline(5.0,color="#8a5a00",ls=":",lw=1.6)
ax[0].text(5.05,2.05,"본 벤치마크 h=5.0\n(주장에 가장 불리)",fontsize=8,color="#8a5a00")
ax[0].text(2.6,1.03,"복사 = 대류",fontsize=8.5)
ax[0].set_xlabel("대류계수 h  [W/(m²·K)]"); ax[0].set_ylabel("$q_{rad}/q_{conv}$")
ax[0].set_title("(a) 주장 A — 문헌 범위 전체에서 비 > 1\nclaim A holds across the reported range",fontsize=10.5)
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3,lw=0.4); ax[0].set_ylim(0.6,2.6)

# (b) 겹치지 않는 두 구간
vals=[4*e*SIG*(0.5*((Tc+273.15)+Tenv))**3 for e in (0.95,0.99) for Tc in (30,37)]
ax[1].barh([1],[5.1-3.1],left=[3.1],height=0.42,color="#4fd1f5",label="h  전신 자연대류 (문헌)")
ax[1].barh([2],[max(vals)-min(vals)],left=[min(vals)],height=0.42,color="#8b5cf6",
           label="$h_r=4εσT_m^3$  (ε 0.95–0.99, $T_s$ 30–37 °C)")
ax[1].plot([5.0],[1],'o',color="#8a5a00",ms=8); ax[1].text(5.15,1.0,"5.0",fontsize=9,color="#8a5a00",va="center")
ax[1].set_ylim(0.4,2.6); ax[1].set_yticks([1,2]); ax[1].set_yticklabels(["대류\nconvection","복사\nradiation"],fontsize=9)
ax[1].set_xlim(2.5,7.2); ax[1].set_xlabel("계수  [W/(m²·K)]")
ax[1].set_title("(b) 두 구간이 겹치지 않는다\nthe intervals do not overlap",fontsize=10.5)
ax[1].legend(fontsize=8,loc="lower right"); ax[1].grid(alpha=0.3,axis="x",lw=0.4)
ax[1].text(5.83,2.33,"5.83 – 6.29",fontsize=8.5,color="#5b3fa0")
ax[1].text(3.15,1.33,"3.1 – 5.1",fontsize=8.5,color="#2b8fae")

# (c) 주장 A 가 멈추는 곳
hh=np.linspace(3,30,300); Ts=36.30+273.15
qr=0.98*SIG*(Ts**4-Tenv**4); share=100*qr/(qr+hh*(Ts-Tenv))
ax[2].plot(hh,share,lw=2.4,color="#8b5cf6")
ax[2].axhline(50,color="k",ls="--",lw=1.2); ax[2].axvspan(3.1,5.1,color="#ffd9a0",alpha=0.5)
for x in (5,10,15,30):
    y=100*qr/(qr+x*(Ts-Tenv)); ax[2].plot([x],[y],'o',color="#8b5cf6",ms=5)
    ax[2].text(x+0.6,y+1.4,"%.0f %%"%y,fontsize=8.5,color="#5b3fa0")
ax[2].text(6.0,52,"복사 = 절반",fontsize=8.5)
ax[2].set_xlabel("대류계수 h  [W/(m²·K)]"); ax[2].set_ylabel("전체 표면 손실 중 복사 비중 [%]")
ax[2].set_title("(c) 주장 A 가 멈추는 곳 — 바람이 불면\nwhere claim A stops: moving air",fontsize=10.5)
ax[2].grid(alpha=0.3,lw=0.4); ax[2].set_ylim(10,72)
fig.suptitle("어떤 주장이 어떤 계수에 의존하는가 / Which claims the coefficients support   ·   "
             "DB-3, 정지 실내 공기 24 °C",fontsize=12.5)
fig.text(0.5,0.015,"주장 A (복사 ≥ 대류, 정지 실내 공기) 는 ε·σ·h 에만 의존한다. "
         "출처를 추적하지 못한 계수는 $T_m^3$ 를 통해서만 들어오며 그 영향은 약 2 % 다.   ·   "
         "Claim A depends only on ε, σ and h.",ha="center",fontsize=9)
fig.tight_layout(rect=[0,0.045,1,0.93])
out="/mnt/user-data/outputs/DB3_주장과계수.png"
fig.savefig(out,dpi=160,facecolor="white"); print(out)
