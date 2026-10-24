# -*- coding: utf-8 -*-
"""GCA: 等宽推进精确对齐 —— 用强匹配锚点拟合 x(i)=x0+adv*i, 再逐字取窗匹配。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in v.read(v.find("charlist_CH","txt")).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
IDX = {c:i for i,c in enumerate(T)}
t = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, A = dxt3_decode(t.read(t.find("fnt_chinese")), 2048, 2048)
PITCH=31; COLS=65
def cell(i):
    r_,c_=i//COLS,i%COLS
    return A[1+PITCH*r_:1+PITCH*r_+PITCH, 1+PITCH*c_:1+PITCH*c_+PITCH]
def norm(a):
    a=a.astype(np.float32); mx=a.max()
    if mx<=0: return None
    ys,xs=np.where(a>mx*0.35)
    if len(ys)==0: return None
    a=a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    if a.shape[0]<5 or a.shape[1]<3: return None
    im=Image.fromarray((a/mx*255).astype(np.uint8)).resize((24,24),Image.LANCZOS)
    z=np.array(im,np.float32)/255.0; z-=z.mean(); n=np.sqrt((z*z).sum())
    return (z/n).ravel() if n>0 else None
TMP=[norm(cell(i)) for i in range(2795)]
IDS=[i for i,x in enumerate(TMP) if x is not None]
TM=np.stack([TMP[i] for i in IDS])

def analyze(path, y0,y1,x0,x1, s, tag):
    im=Image.open(path).convert("RGB")
    a=np.array(im).astype(np.int16)
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    M=(((r>180)&(g>180)&(b>180))|((g>130)&(g>r+40)&(g>b+40)))[y0:y1,x0:x1]
    H,W=M.shape
    # 每个 x 处取整列, 归一化
    wins={}
    for x in range(0,W-28):
        z=norm(M[:,x:x+28].astype(np.float32)*255)
        if z is not None: wins[x]=z
    xs=np.array(sorted(wins))
    Wm=np.stack([wins[x] for x in xs])
    S=TM@Wm.T
    best=np.argmax(S,axis=0); sc=S[best,np.arange(S.shape[1])]
    lab=[IDS[k] for k in best]
    print("\n=== %s  字符数=%d" % (tag, len(s)))
    # 强锚点: 连续 x 内 score 最高者
    peaks=[]
    for i in range(len(xs)):
        lo=max(0,i-6); hi=min(len(xs),i+7)
        if sc[i]>=sc[lo:hi].max()-1e-9 and sc[i]>0.55:
            peaks.append((xs[i], lab[i], sc[i]))
    # 合并相邻峰值
    merged=[]
    for p in peaks:
        if merged and p[0]-merged[-1][0]<=6:
            if p[2]>merged[-1][2]: merged[-1]=p
        else: merged.append(p)
    print("   峰值:", [(x,chr(T[l]),round(s_,2)) for x,l,s_ in merged])
    # 用峰值拟合 x0, adv
    # 对每个候选 (x0, adv) 组合评估: 用 s 的长度
    bestfit=None
    if len(merged)>=3:
        x0c=merged[0][0]; 
        for adv10 in range(280, 360):
            adv=adv10/10.0
            err=0; cnt=0
            for x,l,s_ in merged:
                i=round((x-x0c)/adv)
                if 0<=i<len(s):
                    err+=abs((x0c+i*adv)-x); cnt+=1
            if cnt>=3 and (bestfit is None or err<bestfit[0]): bestfit=(err,adv)
        adv=bestfit[1] if bestfit else 31.5
    else:
        adv=31.5
    x0=merged[0][0] if merged else 0
    print("   拟合: x0=%d adv=%.1f" % (x0, adv))
    res=[]
    for i,ch in enumerate(s):
        xc=x0+i*adv
        lo=int(xc-8); hi=int(xc+9)
        bestp=None
        for x in range(max(0,lo),min(W-28,hi)):
            if x not in wins: continue
            S2=TM@wins[x]; k=int(np.argmax(S2))
            if bestp is None or S2[k]>bestp[2]: bestp=(IDS[k], x, float(S2[k]))
        res.append((ch, IDX[ord(ch)], bestp))
    for ch,slot,bp in res:
        if bp is None: print("   %s slot=%d  ?" % (ch,slot)); continue
        c,x,sc_=bp
        print("   %s slot=%5d  -> cell %5d %s (%.2f)%s" % (ch,slot,c,chr(T[c]),sc_," OK" if c==slot else "  <<< 错位"))

analyze(os.path.join(IMG,"clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"), 690,765, 745,1130, "你的弟兄们需要你的保护", "SUB1")
analyze(os.path.join(IMG,"clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"), 690,795, 565,1400, "你的弟兄们要出去谈几笔生意，保护他们免遭袭击", "SUB3")
