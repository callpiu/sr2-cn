# -*- coding: utf-8 -*-
"""GG7: 取出两句的英文原文 + 汉化记录容量, 为英文降级做准备。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def parse(raw):
    N = struct.unpack_from("<I", raw, 8)[0]
    body = raw[16 + N * 8:]
    ps, cur, i = [], [], 0
    while i + 1 < len(body):
        c = struct.unpack_from(">H", body, i)[0]; i += 2
        if c == 0:
            ps.append(cur); cur = []
        else:
            cur.append(c)
    if cur: ps.append(cur)
    return N, body, ps

def cl(v, nm):
    e = v.find(nm, "txt")
    return [int(s) for s in v.read(e).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()] if e else None

IDS = [0xF284ED87, 0xAF10621E]

# --- 汉化 static_CH ---
pv = Vpp(os.path.join(G, "patch.vpp_pc"))
TH = cl(pv, "charlist_CH")
N, body, ps = parse(pv.read(pv.find("static_CH", "le_strings")))
print("汉化 static_CH: N=%d pieces=%d" % (N, len(ps)))
for tid in IDS:
    lo, hi = tid >> 16, tid & 0xFFFF
    for k, p in enumerate(ps):
        if len(p) >= 2 and ((p[0] == lo and p[1] == hi) or (p[0] == hi and p[1] == lo)):
            slots = p[2:]
            print("\n[汉化] ID 0x%08X  piece#%d  总 u16=%d  槽位=%d" % (tid, k, len(p), len(slots)))
            print("   文本: %s" % "".join(chr(TH[c - 32]) if 0 <= c - 32 < len(TH) else "?" for c in slots))
            break

# --- 英文原文 ---
for tag, path, clname in (("patch.orig/static_US", r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_US"),
                          ("Mods/static_US", os.path.join(G, "Mods", "static_US.le_strings"), "charlist_US")):
    try:
        if path.endswith(".le_strings"):
            raw = open(path, "rb").read()
            TU = cl(Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"), clname)
        else:
            v = Vpp(path); TU = cl(v, clname)
            e = v.find("static_US", "le_strings")
            if not e: print("\n[%s] 无 static_US" % tag); continue
            raw = v.read(e)
    except Exception as ex:
        print("\n[%s] 失败 %s" % (tag, ex)); continue
    N2, b2, ps2 = parse(raw)
    print("\n[%s] charlist_US=%s pieces=%d" % (tag, len(TU) if TU else None, len(ps2)))
    for tid in IDS:
        lo, hi = tid >> 16, tid & 0xFFFF
        for k, p in enumerate(ps2):
            if len(p) >= 2 and ((p[0] == lo and p[1] == hi) or (p[0] == hi and p[1] == lo)):
                slots = p[2:]
                s = "".join(chr(TU[c - 32]) if TU and 0 <= c - 32 < len(TU) else "?" for c in slots)
                print("   ID 0x%08X  piece#%d  槽位=%d  (%d 字符)" % (tid, k, len(slots), len(s)))
                print("      %s" % s)
                break
        else:
            print("   ID 0x%08X 未找到" % tid)
