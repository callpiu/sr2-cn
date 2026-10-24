# -*- coding: utf-8 -*-
# 按内容搜索: 含"弟兄/保护"(正确) 或 "任璨"(乱码) 的记录
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def cl_from(buf):
    return [int(x) for x in re.findall(rb'\d+', buf)]

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

def dec(slots):
    o = []
    for w in slots:
        if w < 0x20: o.append('·'); continue
        i = w - 0x20
        o.append(chr(LC[i]) if i < len(LC) else '?')
    return ''.join(o)

KEYS = ["弟兄", "保护", "任璨", "你的弟兄"]
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    rs = parse(cn.read(e))
    for h, s in rs:
        t = dec(s)
        for k in KEYS:
            if k in t:
                print("[%s] %08X len=%d  KEY=%s" % (nm, h, len(s), k))
                print("   %s" % t[:80])
                print("   slots:", [hex(x) for x in s])
                break
print("done")
