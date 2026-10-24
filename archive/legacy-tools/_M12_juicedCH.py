# -*- coding: utf-8 -*-
"""精确破解 juiced_CH.le_strings 的 slot 基址。
已知其它语言 juiced_XX 用 slot=idx+32 解码完美(它们无中文, 全是拉丁字母)。
juiced_CH 有中文, 用它反推正确的 slot 基址。
"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
CL=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]

raw=open(G+r'\Mods\JUICED - Strings\juiced_CH.le_strings','rb').read()
magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
oa=16+buckets*8
recs=[]
for i in range(count):
    o=struct.unpack_from('<I',raw,oa+i*4)[0]
    h=struct.unpack_from('<H',raw,o)[0]
    p=o+4; us=[]
    while p+1<len(raw):
        u=struct.unpack_from('>H',raw,p)[0]; p+=2
        if u==0:break
        us.append(u)
    recs.append((h,us))

print("记录数=",len(recs))
for h,us in recs:
    print("\n=== h=%04X ===" % h)
    print("  units:", " ".join("%04X"%u for u in us))
    for delta in (0,32,64,224,256,128,-32):
        out=[]
        for u in us:
            if u<0x100: out.append(chr(u))
            else:
                i=u-delta
                out.append(chr(CL[i]) if 0<=i<len(CL) else '.')
        print("  d=%-4d %s" % (delta, "".join(out)[:75]))
