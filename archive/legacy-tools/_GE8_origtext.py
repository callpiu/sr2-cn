# -*- coding: utf-8 -*-
"""GE8: 完整解码 ORIG / HAN static_CH, 搜索关键词; 并解析索引表。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"

def load(path):
    v = Vpp(path)
    T = [int(s) for s in v.read(v.find("charlist_CH","txt")).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
    raw = v.read(v.find("static_CH","le_strings"))
    return T, raw

def pieces_of(raw):
    N = struct.unpack_from("<I", raw, 8)[0]
    body = raw[16 + N*8:]
    ps, cur, i = [], [], 0
    while i + 1 < len(body):
        c = struct.unpack_from(">H", body, i)[0]; i += 2
        if c == 0:
            ps.append(cur); cur = []
        else:
            cur.append(c)
    if cur: ps.append(cur)
    return N, body, ps

def dec(cds, T):
    return "".join(chr(T[c-32]) if 0 <= c-32 < len(T) else "?" for c in cds[2:])

for tag, p in (("ORIG", ORIG), ("HAN", HAN)):
    T, raw = load(p)
    N, body, ps = pieces_of(raw)
    print("="*72)
    print("[%s] charlist=%d  N=%d  body=%d  pieces=%d" % (tag, len(T), N, len(body), len(ps)))
    # 索引表前 4 项
    print("  索引表前4项:", [struct.unpack_from("<II", raw, 16+8*k) for k in range(4)])
    # 索引表里找 ID
    for k in range(N):
        iid = struct.unpack_from("<I", raw, 16+8*k)[0]
        if iid == 0xF284ED87:
            print("  索引表 #%d -> ID 0xF284ED87, off=%d" % (k, struct.unpack_from("<I", raw, 16+8*k+4)[0]))
            break
    else:
        print("  索引表中无 0xF284ED87")
    for kw in ("保護", "保护", "弟兄", "兄弟", "homies", "袭击"):
        hits = [k for k, c in enumerate(ps) if kw in dec(c, T)]
        print("  关键词 %-6s 命中 %d 条: %s" % (kw, len(hits), hits[:5]))
        for h in hits[:2]:
            print("        #%d: %s" % (h, dec(ps[h], T)))
