# -*- coding: utf-8 -*-
"""检查 static_CH 中"不可读"的记录（第六轮说650条），看它们的特征。"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CL=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]
N=len(CL)
raw=v.read(v.find('static_CH','le_strings'))
magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
tbase=16+buckets*8
offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count)]
print("static_CH count=%d" % count)
def dec(o):
    p=o+4; units=[]; ok=True
    while p+1<len(raw):
        u=struct.unpack_from('>H',raw,p)[0]; p+=2
        if u==0: break
        units.append(u)
    out=[]
    for u in units:
        if u<0x100: out.append(chr(u))
        else:
            i=u-32
            if 0<=i<N: out.append(chr(CL[i]))
            else: out.append('?'); ok=False
    return ''.join(out), ok

bad=[]
for k,o in enumerate(offs):
    if not (0<o<len(raw)-4): 
        bad.append((k,o,'OOB_OFF','')); continue
    s,ok=dec(o)
    # 判断是否有不可打印
    if not ok or any(not (c.isprintable() or c in '\r\n\t') for c in s):
        bad.append((k,o,'NONPRINT',s[:60]))
print("异常记录数 =", len(bad))
for k,o,why,s in bad[:30]:
    print("  #%d off=0x%X %s: %r" % (k,o,why,s))
