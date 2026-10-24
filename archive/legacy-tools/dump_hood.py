# -*- coding: utf-8 -*-
"""dump 0x019F0ED8 与 0x01AC1094 附近区域结构 —— 找 hood/district 名表"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(c): return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)

def dump_records(lo,hi,label):
    print('=== %s  [0x%08X, 0x%08X) ==='%(label,lo,hi))
    i=lo
    out=[]
    while i<hi:
        o=[];j=i
        while j+2<=n:
            w=struct.unpack_from('>H',b,j)[0]
            if w==0: break
            o.append(w); j+=2
        if j+2>n: break
        t=''.join(dec(x) for x in o)
        out.append((i,t))
        i=j+2
    for at,t in out:
        print('  0x%08X  %-14r slots=%s'%(at,t,[hex(x) for x in
              struct.unpack_from('>%dH'%(len(t) or 1),b,at)[:8]]))
    print('  共 %d 条'%len(out))
    print()
    return out

# 单字「城」第一条附近 —— 观察该区域是否是「单字名表」
dump_records(0x019F0E00,0x019F1000,'A: 0x019F0E00 区域')
dump_records(0x01AC1000,0x01AC1200,'B: 0x01AC1000 区域')