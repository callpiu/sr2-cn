# -*- coding: utf-8 -*-
"""GE5: 列出各 VPP 内所有 le_strings 条目, 并在其中搜索目标 ID (u16 对 F284/ED87)。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"
G    = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def parse(raw):
    if len(raw) < 16: return []
    N = struct.unpack_from("<I", raw, 8)[0]
    if N > 100000: return []
    body = raw[16 + N * 8:]
    pieces, cur, i = [], [], 0
    while i + 1 < len(body):
        c = struct.unpack_from(">H", body, i)[0]; i += 2
        if c == 0:
            pieces.append(cur); cur = []
        else:
            cur.append(c)
    if cur: pieces.append(cur)
    return pieces

def probe(tag, path):
    print("=" * 72)
    print("[%s] %s" % (tag, os.path.basename(path)))
    v = Vpp(path)
    ents = v.entries()
    # charlist
    T = None
    ce = v.find("charlist_CH", "txt")
    if ce:
        T = [int(s) for s in v.read(ce).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
    print("  charlist_CH =", len(T) if T else "无")
    for k, e in enumerate(ents):
        nm, ex_ = e["name"] or "", e["ext"] or ""
        if "le_strings" not in ex_ and "le_strings" not in nm:
            continue
        raw = v.read(e)
        pieces = parse(raw)
        hit = None
        for pi, p in enumerate(pieces):
            if len(p) >= 2 and ((p[0] == 0xF284 and p[1] == 0xED87) or (p[0] == 0xED87 and p[1] == 0xF284)):
                hit = (pi, p); break
        mark = ""
        if hit:
            pi, p = hit
            body = p[2:]
            s = "".join(chr(T[c - 32]) if T and 0 <= c - 32 < len(T) else "?" for c in body)
            mark = "   <== HIT piece#%d  %s" % (pi, s)
        print("  %-22s %-14s %9d  pieces=%5d%s" % (nm, ex_, len(raw), len(pieces), mark))

probe("ORIG-patch", ORIG)
probe("HAN-patch", HAN)
probe("CUR-patch", os.path.join(G, "patch.vpp_pc"))
