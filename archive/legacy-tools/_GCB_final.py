# -*- coding: utf-8 -*-
"""GCB: 用 run 切分 + 均匀推进(~31px) 精确定位每个字, 输出 (字, 槽位, 观测格子)。"""
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

def go(path,y0,y1,x0,x1,s,tag):
    a=np.array(Image.open(path).convert("RGB")).astype(np.int16)
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    M=(((r>180)&(g>180)&(b>180))|((g>130)&(g>r+40)&(g>b+40)))[y0:y1,x0:x1]
    H,W=M.shape
    prof=M.sum(axis=0)
    runs=[];inrun=False;gap=0
    for x in range(W):
        if prof[x]>0:
            if not inrun: inrun=True;st=x
            gap=0
        else:
            if inrun:
                gap+=1
                if gap>=3: runs.append((st,x-gap+1));inrun=False
    if inrun: runs.append((st,W))
    print("\n=== %s  字符=%d  run数=%d" % (tag,len(s),len(runs)))
    units=[]
    for (st,en) in runs:
        w=en-st; k=max(1,int(round(w/31.0)))
        for j in range(k): units.append((st+w*j//k, st+w*(j+1)//k))
    print("   摊开单元=%d  首单元x=%d 末单元x=%d" % (len(units),units[0][0],units[-1][0]))
    # 拟合 x0,adv: 用首末单元
    x0=units[0][0]; adv=(units[-1][0]-x0)/max(1,(len(s)-1))
    print("   拟合 x0=%d adv=%.2f" % (x0,adv))
    out=[]
    for i,ch in enumerate(s):
        xc=x0+i*adv
        lo=int(xc-6); hi=int(xc+7); best=None
        for x in range(max(0,lo),min(W-30,hi)):
            z=norm(M[:,x:x+30].astype(np.float32)*255)
            if z is None: continue
            S=TM@z; k=int(np.argmax(S))
            if best is None or S[k]>best[2]: best=(IDS[k],x,float(S[k]))
        out.append((ch,IDX[ord(ch)],best))
    for ch,slot,bp in out:
        if bp is None: print("   %s slot=%5d ?"%(ch,slot)); continue
        c,x,sc=bp
        print("   %s slot=%5d -> cell %5d %s (%.2f) %s"%(ch,slot,c,chr(T[c]),sc,"OK" if c==slot else "X"))

go(os.path.join(IMG,"clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"),690,765,745,1130,"你的弟兄们需要你的保护","SUB1")
go(os.path.join(IMG,"clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"),690,795,565,1400,"你的弟兄们要出去谈几笔生意，保护他们免遭袭击","SUB3")
