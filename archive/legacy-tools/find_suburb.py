# -*- coding: utf-8 -*-
"""1) 英文表里搜 Suburb  2) static_CH 内找精确等于「城」的记录  3) 各 CH 表里的单字「城」"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

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

# ---- 1) 英文表搜 Suburb ----
v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
print('=== 英文表搜 Suburb ===')
for tname in ('static_US','voice_script_US','platform_pc_US'):
    try:
        e=v2.find(tname,'le_strings')
    except Exception:
        print('  %s: 无此条目'%tname); continue
    d=bytes(v2.read(e))
    for kw in ('Suburb','Outskirt','Downtown'):
        p=kw.encode('utf-16-le'); c=d.count(p)
        if c: print('  %-18s %-10s -> %d'%(tname,kw,c))

# ---- 2) 各 CH 表里精确单字「城」的记录 ----
print()
print('=== 汉化表里精确等于「城」的记录 ===')
S1=struct.pack('>H',S('城'))
PAT=struct.pack('>2H',S('城'),0x0000)
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
for tname in ('static_CH','voice_script_CH','platform_pc_CH','juiced_CH'):
    try:
        e=v.find(tname,'le_strings')
    except Exception:
        print('  %s: 无'%tname); continue
    d=bytes(v.read(e))
    hits=[]; st=0
    while True:
        i=d.find(PAT,st)
        if i<0: break
        hits.append(i); st=i+1
    print('  %-18s blob=%-8d 单字「城」记录=%d %s'%(tname,len(d),len(hits),
          [hex(x) for x in hits[:8]]))

# ---- 3) static_CH 内 base 换算 ----
e=v.find('static_CH','le_strings')
base=e['body']-len(bytes(v.read(e)))
print()
print('static_CH body=%d, 推算 blob 在文件内 base=0x%08X'%(e['body'],base))
print('  验证：迷雾巷 file 0x01C2D86A - blob 0x61698 = 0x%08X'%(0x01C2D86A-0x61698))