# -*- coding: utf-8 -*-
"""全 blob 顺序扫描记录，逐条与 static_US 同位置对齐，查 Suburbs / 城郊 对应关系"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(errors='replace')
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
def safe(t): return t.encode('utf-8','replace').decode('utf-8','replace')

v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
v2=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
US=bytes(v2.read(v2.find('static_US','le_strings')))

def scan_all(blob, is_slot):
    """顺序扫出所有以 0000 开头（记录头）的记录，返回 [(off, text)]"""
    res=[]
    n=len(blob); i=0
    while i+2<=n:
        # 记录起点 = 前面是 0000
        i+=2
        o=[]; j=i
        while j+2<=n:
            w=struct.unpack_from('>H',blob,j)[0]
            if w==0: break
            o.append(w); j+=2
        if j+2>n: break
        if o:
            t=''.join(dec(x) for x in o) if is_slot else ''.join(chr(x) for x in o)
            res.append((i,t))
        i=j+2
    return res

A=scan_all(CH,True)
B=scan_all(US,False)
print('CH 顺序扫出记录 =',len(A))
print('US 顺序扫出记录 =',len(B))
print()
# 找 CH 里所有含「城郊」的
print('=== CH 含「城郊」→ 同序号 US ===')
na=len(A); nb=len(B)
found=0
for k,(off,t) in enumerate(A):
    if '城郊' in t:
        found+=1
        en = B[k][1] if k<nb else '<无>'
        print('  #%-5d off=0x%06X CN=%-34s EN=%s'%(k,off,t[:34].replace('\n',''),safe(en[:60].replace('\n',' '))))
print('  共 %d 条'%found)
print()
print('=== US 含 Suburb → 同序号 CH ===')
found2=0
for k,(off,t) in enumerate(B):
    if 'Suburb' in t:
        found2+=1
        cn = A[k][1] if k<na else '<无>'
        print('  #%-5d EN=%-46s CN=%s'%(k,safe(t[:46].replace('\n',' ')),cn[:34]))
print('  共 %d 条'%found2)