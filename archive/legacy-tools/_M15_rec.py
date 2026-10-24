# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CL=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]

raw=open(G+r'\Mods\JUICED - Strings\juiced_CH.le_strings','rb').read()
magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
print("count=%d buckets=%d" % (count,buckets))
# 记录偏移表位置候选
for tbase in (16+buckets*8, 16, 16+buckets*4):
    offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count)]
    ok=all(0<o<len(raw) for o in offs)
    print("tbase=0x%X offs=%s ok=%s" % (tbase, [hex(o) for o in offs[:6]], ok))
print()
# 用 0x110
tbase=16+buckets*8
offs=[struct.unpack_from('<I',raw,tbase+i*4)[0] for i in range(count)]
print("记录偏移:", [hex(o) for o in offs])
print()
def dec(o, skip, delta=32):
    p=o+skip; units=[]
    while p+1<len(raw):
        u=struct.unpack_from('>H',raw,p)[0]; p+=2
        if u==0:break
        units.append(u)
    out=[]
    for u in units:
        if u<0x100: out.append(chr(u))
        else:
            i=u-delta
            out.append(chr(CL[i]) if 0<=i<len(CL) else '?')
    return ''.join(out)

for o in offs:
    print("off=0x%03X raw: %s" % (o, raw[o:o+20].hex(' ').upper()))
    for skip in (0,2,4):
        print("     skip=%d: %s" % (skip, dec(o,skip)[:66]))
    print()
