# -*- coding: utf-8 -*-
# 检查 voice_script_CH.le_strings 的槽位编码是否正确
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def cl_from(buf): return [int(x) for x in re.findall(rb'\d+', buf)]

def parse(data):
    if len(data) < 12: return []
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    if off + count*4 > len(data): return []
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    out = []; n = len(data)
    for p in ptrs:
        if p == 0 or p >= n - 4: continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= n:
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        out.append(((id1 << 16) | id2, slots))
    return out

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
LC = cl_from(cn.read(cn.find("charlist_CH", "txt")))
print("charlist_CH =", len(LC))

def dec(slots, off=0x20):
    o=[]
    for w in slots:
        if w < off: o.append('·'); continue
        i=w-off; o.append(chr(LC[i]) if 0<=i<len(LC) else '?')
    return ''.join(o)

for e in cn.entries():
    if e['ext'].lower()!='le_strings': continue
    nm = e['name']+'.'+e['ext']
    if 'voice' not in nm.lower(): continue
    rs = parse(cn.read(e))
    print("\n=== %s : %d 条 ===" % (nm, len(rs)))
    # 统计槽位分布
    mx = max((max(s) for _,s in rs if s), default=0)
    print("   max slot =", hex(mx), mx)
    print("   前 12 条解码(off=0x20):")
    for h, s in rs[:12]:
        print("     %08X len=%3d  %s" % (h, len(s), dec(s)[:60]))
    print("   前 12 条解码(off=0x00):")
    for h, s in rs[:6]:
        print("     %08X len=%3d  %s" % (h, len(s), dec(s,0)[:60]))
