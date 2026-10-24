# -*- coding: utf-8 -*-
# 只读: 追踪当前 patch 里这两条字幕到底指向哪条记录
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
P = os.path.join(G, "patch.vpp_pc")

def nums(buf): return [int(x) for x in re.findall(rb'\d+', buf)]

def dec(slots, cl):
    out=[]
    for w in slots:
        i=w-0x20
        out.append(chr(cl[i]) if 0<=i<len(cl) else '?')
    return ''.join(out)

def parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    po = 12 + buckets*8
    out=[]
    for idx in range(count):
        p=struct.unpack_from("<I", data, po+idx*4)[0]
        id1,id2=struct.unpack_from("<HH", data, p)
        q=p+4; slots=[]
        while q+2<=len(data):
            w=struct.unpack_from(">H", data, q)[0]
            if w==0: break
            slots.append(w); q+=2
        raw4=data[p:p+4]
        out.append((idx,p,id1,id2,raw4,slots))
    return buckets,count,out

v=Vpp(P)
cl=nums(v.read(v.find("charlist_CH","txt")))
for table in ["static_CH","static_US"]:
    d=v.read(v.find(table,"le_strings"))
    buckets,count,rows=parse(d)
    print("\n===", table, "buckets", buckets, "count", count, "size", len(d), "===")
    hit=0
    for idx,p,id1,id2,raw4,slots in rows:
        t=dec(slots, cl)
        if ("弟兄" in t) or ("homies" in t) or ("Special" in t) or ("特殊弟兄" in t):
            h_a=(id1<<16)|id2
            h_b=(id2<<16)|id1
            h_le=struct.unpack("<I", raw4)[0]
            h_be=struct.unpack(">I", raw4)[0]
            print("idx=%5d ptr=%08x id1=%04x id2=%04x hA=%08X hB=%08X le=%08X be=%08X slots=%3d  %s" % (idx,p,id1,id2,h_a,h_b,h_le,h_be,len(slots),t[:130]))
            hit+=1
            if hit>=30: break
    print("hits", hit)
