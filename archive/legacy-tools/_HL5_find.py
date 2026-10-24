# -*- coding: utf-8 -*-
# 全盘扫描: 定位槽位序列 == 正确 或 == 显示 的那条记录
import os, sys, re, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

CORRECT = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]
DISPLAY = [368,1816,442,999,394,2688,2300,368,1816,386,2374]

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

def sub(seq, pat):
    L = len(pat)
    for k in range(len(seq) - L + 1):
        if seq[k:k+L] == pat: return k
    return -1

files = sorted(glob.glob(os.path.join(G, "*.vpp_pc")))
print("scan", len(files), "vpp_pc")
for f in files:
    try:
        v = Vpp(f)
    except Exception as ex:
        print("  !!", os.path.basename(f), ex); continue
    ents = [e for e in v.entries() if e['ext'].lower() == 'le_strings']
    if not ents: continue
    base = os.path.basename(f)
    for e in ents:
        nm = e['name'] + '.' + e['ext']
        try:
            rs = parse(v.read(e))
        except Exception:
            continue
        for h, s in rs:
            k1 = sub(s, CORRECT)
            k2 = sub(s, DISPLAY)
            if k1 >= 0 or k2 >= 0:
                print("  >>> [%s / %s] %08X  len=%d  correct@%d display@%d" % (base, nm, h, len(s), k1, k2))
                print("      slots:", [hex(x) for x in s])
    print("  scanned", base, "le_strings entries =", len(ents))
print("done")
