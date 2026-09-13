# -*- coding: utf-8 -*-
"""[EN] Regenerates db3_numerical_results.png from a live run of the solver.
Run from the solver repository root with the DB-3 example on the path:

    PYTHONPATH=src:examples:examples/db3 python make_numerical_figure.py

[KO] 솔버를 실제로 돌려 db3_numerical_results.png 를 다시 만든다.
솔버 저장소 루트에서 DB-3 예제를 경로에 넣고 실행한다.
"""
import numpy as np, sys, matplotlib, warnings
sys.path[:0]=["examples/db3"]
warnings.filterwarnings("ignore")
matplotlib.use("Agg")
def _use_cjk_font():
    """Pick a font that can draw Korean, wherever we are running.
    어디서 실행하든 한글을 그릴 수 있는 폰트를 고른다. 없으면 기본 폰트로 물러난다."""
    import os
    from matplotlib import font_manager, rcParams
    for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
              "/System/Library/Fonts/AppleSDGothicNeo.ttc",
              "/Library/Fonts/AppleGothic.ttf",
              "C:/Windows/Fonts/malgun.ttf"):
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                rcParams["font.family"] = font_manager.FontProperties(fname=p).get_name()
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
import matplotlib.pyplot as plt, matplotlib.tri as mtri
import db3_properties as P
import db3_verify as V
CASES=[("약함 weak ×0.1",0.1,"#3b7dd8"),("정상 nominal ×1",1.0,"#2ca02c"),("강함 strong ×10",10.0,"#d62b4a")]
data={}
for lab,sc,col in CASES:
    st,ex=V.exact(sc); recs=[]
    for rf in (1,2,4):
        m,T,pw,react,hist=V.run(rf,sc)
        Tex=ex["T_of_x"](m.nodes[:,1]); rvar=0.0
        for z in np.unique(np.round(m.nodes[:,1],12)):
            s=np.abs(m.nodes[:,1]-z)<1e-14
            if s.sum()>1: rvar=max(rvar,float(T[s].max()-T[s].min()))
        Pin=pw["source"]+sum(v for k,v in pw.items() if k not in ("source","radiation_net"))
        recs.append(dict(rf=rf,m=m,T=T,Tex=Tex,err=float(np.abs(T-Tex).max()),rvar=rvar,
                         hist=hist,eres=abs(Pin+react)/max(abs(Pin),1e-30),pw=pw))
    data[lab]=(sc,col,ex,recs)
fig=plt.figure(figsize=(15.8,10.6))
gs=fig.add_gridspec(3,3,height_ratios=[1.15,1.0,0.70],hspace=0.46,wspace=0.34,
                    left=0.055,right=0.975,top=0.905,bottom=0.045)
ax=fig.add_subplot(gs[0,0]); x=np.linspace(0,P.L_TOT,400)
for lab,(sc,col,ex,recs) in data.items():
    ax.plot(x*1e3,ex["T_of_x"](x)-273.15,color=col,lw=2.0,label="정확해 "+lab)
    r=recs[0]; sel=np.abs(r["m"].nodes[:,0])<1e-12
    ax.plot(r["m"].nodes[sel,1]*1e3,r["T"][sel]-273.15,'o',color=col,ms=4.2,mfc='white',mew=1.3)
for b in (P.L_SUB*1e3,(P.L_SUB+P.L_DER)*1e3): ax.axvline(b,color="#aaa",ls="--",lw=0.8)
ax.plot([],[],'o',color="#555",mfc='white',mew=1.3,ms=4.2,label="계산 (h 격자 절점)")
ax.set_xlabel("깊이 depth [mm]"); ax.set_ylabel("T [°C]")
ax.set_title("(a) 온도 분포 — 정확해와 계산\nprofile: exact vs computed",fontsize=10)
ax.legend(fontsize=7.6,loc="lower left"); ax.grid(alpha=0.3,lw=0.4)
ax=fig.add_subplot(gs[0,1]); hs=np.array([P.characteristic_h(r)*1e3 for r in (1,2,4)])
for lab,(sc,col,ex,recs) in data.items():
    e=np.array([r["err"] for r in recs])
    ax.loglog(hs,e,'o-',color=col,lw=1.8,ms=5,label="%s  p=%.2f"%(lab,np.log2(e[1]/e[2])))
ref=data["정상 nominal ×1"][3][0]["err"]
ax.loglog(hs,ref*(hs/hs[0])**4,'--',color="#888",lw=1.2,label="기울기 4 (절점 초수렴)")
ax.set_xlabel("최소 요소 크기 h [mm]"); ax.set_ylabel("절점 L∞ 오차 [K]")
ax.set_title("(b) 격자 수렴 — 허용오차가 아니라 차수로 판정\nconvergence: order, not tolerance",fontsize=10)
ax.legend(fontsize=7.6); ax.grid(alpha=0.3,which="both",lw=0.4)
ax=fig.add_subplot(gs[0,2]); sc,col,ex,recs=data["정상 nominal ×1"]
for r,c2 in zip(recs,("#c9d6e8","#6b93c9","#1f4e8c")):
    sel=np.abs(r["m"].nodes[:,0])<1e-12; o=np.argsort(r["m"].nodes[sel,1])
    ax.semilogy(r["m"].nodes[sel,1][o]*1e3,np.abs(r["T"][sel]-r["Tex"][sel])[o]+1e-16,'-',
                color=c2,lw=1.5,label="h/%d"%r["rf"])
for b in (P.L_SUB*1e3,(P.L_SUB+P.L_DER)*1e3): ax.axvline(b,color="#aaa",ls="--",lw=0.8)
ax.set_xlabel("깊이 depth [mm]"); ax.set_ylabel("|T − T_exact| [K]")
ax.set_title("(c) 오차는 어디에 있는가 (정상 관류)\nwhere the error lives",fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=0.3,which="both",lw=0.4)
ax=fig.add_subplot(gs[1,0])
for lab,(sc,col,ex,recs) in data.items():
    h=recs[-1]["hist"]; ax.semilogy(range(1,len(h)+1),h,'o-',color=col,lw=1.8,ms=5,label=lab)
ax.set_xlabel("Newton 반복"); ax.set_ylabel("max |ΔT| [K]")
ax.set_title("(d) Newton 수렴 — 복사의 4εσT³ 항 포함\nNewton with the radiative Jacobian",fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=0.3,which="both",lw=0.4)
ax=fig.add_subplot(gs[1,1]); r=data["정상 nominal ×1"][3][1]; m=r["m"]
SUB=[(0,4,8,7),(4,1,5,8),(8,5,2,6),(7,8,6,3)]; tri=[]
for c in m.elems:
    for q in SUB:
        a,b,d,e2=(int(c[i]) for i in q); tri.append((a,b,d)); tri.append((a,d,e2))
t=mtri.Triangulation(m.nodes[:,0]*1e3,m.nodes[:,1]*1e3,np.array(tri))
cf=ax.tricontourf(t,r["T"]-273.15,levels=30,cmap="inferno")
cb=fig.colorbar(cf,ax=ax,fraction=0.040,pad=0.02); cb.ax.tick_params(labelsize=7.5)
ax.set_aspect("equal"); ax.set_xlabel("r [mm]"); ax.set_ylabel("z [mm]")
ax.set_title("(e) 2차원 온도장 [°C] — 반경 변화 %.1e K\n2D field: radial variation (exact: 0)"%r["rvar"],fontsize=10)
ax=fig.add_subplot(gs[1,2]); w=0.25
for i,(lab,(sc,col,ex,recs)) in enumerate(data.items()):
    ax.bar(np.arange(3)+(i-1)*w,[max(rr["rvar"],1e-16) for rr in recs],w,color=col,label=lab)
ax.set_yscale("log"); ax.set_xticks(range(3)); ax.set_xticklabels(["h","h/2","h/4"])
ax.set_ylim(1e-14,3e-8)
ax.axhline(1e-9,color="#c00",ls="--",lw=1.0); ax.text(-0.42,1.4e-9,"시험 기준 1e-9",fontsize=8,color="#c00")
ax.set_ylabel("최대 반경 변화 [K]",labelpad=2)
ax.set_title("(f) 허위 반경 변화 — 정확해는 0\nspurious radial variation",fontsize=10)
ax.legend(fontsize=7.4,loc="lower right"); ax.grid(alpha=0.3,axis="y",which="both",lw=0.4)
ax=fig.add_subplot(gs[2,:]); ax.axis("off")
rows=[["case","κL 피하/진피","정확해 T_s [K]","계산 T_s [K]","차이 [K]","L∞ 오차 [K] (h/4)",
       "관측 차수 p","에너지 잔차","반경 변화 [K]"]]
for lab,(sc,col,ex,recs) in data.items():
    r=recs[-1]; sel=np.abs(r["m"].nodes[:,1]-P.L_TOT)<1e-14
    kl=[np.sqrt(w2*sc*P.RHO_CB/k)*L for n,L,k,w2 in P.LAYERS if w2>0]
    rows.append([lab.split()[0],"%.2f / %.2f"%(kl[0],kl[1]),"%.7f"%ex["T_surface"],
                 "%.7f"%r["T"][sel].mean(),"%+.1e"%(r["T"][sel].mean()-ex["T_surface"]),
                 "%.2e"%r["err"],"%.2f"%np.log2(recs[1]["err"]/recs[2]["err"]),
                 "%.1e"%r["eres"],"%.1e"%r["rvar"]])
tb=ax.table(cellText=rows[1:],colLabels=rows[0],loc="center",cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1.0,1.6)
for j in range(len(rows[0])): tb[0,j].set_facecolor("#D9E2F3"); tb[0,j].set_text_props(weight="bold")
ax.set_title("(g) 정확해 대조 종합 — 최밀 격자 h/4",fontsize=10.5,pad=16)
fig.suptitle("DB-3 수치해석 결과 / Numerical results — 다층 피부 · 관류 · 대류 + 복사   "
             "(yuchiri-axirad2D v1.1.0, 9절점 사각형)",fontsize=13)
out="/mnt/user-data/outputs/DB3_수치해석결과.png"
fig.savefig(out,dpi=155,facecolor="white"); print(out)
