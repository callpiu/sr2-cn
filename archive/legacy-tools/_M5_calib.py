# -*- coding: utf-8 -*-
"""用 ASCII+中文混排记录精确标定 slot 基址。
原理: ASCII 部分 unit<0x100 直通 → 可读; 中文部分 unit>=0x100 → slot。
     若 slot 基址错，中文会乱而 ASCII 正常（正是我们的症状！）
"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
CL=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]
cp2i={cp:i for i,cp in enumerate(CL)}

def recs(raw):
    magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
    oa=16+buckets*8
    d={}
    for i in range(count):
        o=struct.unpack_from('<I',raw,oa+i*4)[0]
        if not(0<=o<len(raw)-4):continue
        h=struct.unpack_from('<H',raw,o)[0]
        p=o+4; us=[]
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0:break
            us.append(u)
        d.setdefault(h,us)
    return d

ST=recs(v.read(v.find('static_CH','le_strings')))

# 取 h=739B ([format][color:red]新闻直升机...)
for h in (0x739B, 0x0F84, 0x40C4):
    us=ST.get(h)
    if not us: continue
    print("=== h=%04X 原始 unit ===" % h)
    print("  ", " ".join(("%04X"%u) for u in us[:30]))
    # 分离 ASCII 与 slot
    asc=[u for u in us if u<0x100]
    slots=[u for u in us if u>=0x100]
    print("  ASCII units: %s" % "".join(chr(u) for u in asc)[:60])
    print("  中文 slot 值: %s" % " ".join("%d"%s for s in slots[:20]))
    # 用不同 delta 试
    for delta in (0, 32, 224, 256):
        out=[]
        for u in us:
            if u<0x100: out.append(chr(u))
            else:
                i=u-delta
                out.append(chr(CL[i]) if 0<=i<len(CL) else '.')
        print("  delta=%-4d -> %s" % (delta, "".join(out)[:70]))
    print()
