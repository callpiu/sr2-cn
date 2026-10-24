# -*- coding: utf-8 -*-
"""GC3: 解出 static_CH 里那两条字幕的准确中文, 并给出每个字的槽位。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("charlist_CH", "txt")
T = [int(s) for s in v.read(e).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
print("charlist:", len(T))

def load_le(p, name):
    vv = Vpp(p)
    ee = vv.find(name, "le_strings")
    return vv.read(ee)

raw = load_le(os.path.join(G, "patch.vpp_pc"), "static_CH")
print("static_CH:", len(raw), "magic", raw[:4].hex())
N = struct.unpack_from("<I", raw, 8)[0]
lang = struct.unpack_from("<I", raw, 12)[0]
print("N =", N, " lang =", lang, " body@", 16 + N * 8)

body = raw[16 + N * 8:]

# 按 0 分隔切成条
pieces = []
cur = []
i = 0
while i + 1 < len(body):
    c = struct.unpack_from(">H", body, i)[0]
    i += 2
    if c == 0:
        pieces.append(cur); cur = []
    else:
        cur.append(c)
if cur: pieces.append(cur)
print("pieces:", len(pieces))

def dec(codes):
    out = []
    for c in codes[2:]:      # 前 2 个 u16 = 字符串 ID
        idx = c - 32
        out.append(chr(T[idx]) if 0 <= idx < len(T) else "?")
    return "".join(out)

for pid in (3461, 5231):
    if pid < len(pieces):
        cds = pieces[pid]
        print("\n[piece #%d] codes=%s" % (pid, cds))
        print("   ID u16:", cds[:2], " -> hex 0x%04X%04X" % (cds[0], cds[1]))
        print("   文本:", dec(cds))
        print("   槽位:", [c - 32 for c in cds[2:]])

# 顺便找含 "弟兄" 的所有条目
print("\n--- 搜索所有含 '弟兄' 的条目 ---")
hits = 0
for pid, cds in enumerate(pieces):
    s = dec(cds)
    if "弟兄" in s:
        hits += 1
        print("  #%d  %s" % (pid, s))
        print("      codes:", cds[2:])
        print("      slots:", [c - 32 for c in cds[2:]])
        if hits > 8: break
