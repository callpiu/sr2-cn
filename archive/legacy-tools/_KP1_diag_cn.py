# -*- coding: utf-8 -*-
# 汉化构建诊断：charlist 项数 / 6 条记录的正确文本 / 探测 OFFSET
import os, re, struct, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, sheet, png_gray, Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
P = os.path.join(G, "patch.vpp_pc")
import hashlib
print("patch.vpp_pc  size=%d  md5=%s" % (os.path.getsize(P), hashlib.md5(open(P, "rb").read()).hexdigest()))

f = Font(P)
print("charlist_CH 项数 = %d" % len(f.charlist))
print("图集 = %s.%s size=%d" % (f.atlas_entry["name"], f.atlas_entry["ext"], f.atlas_entry["size"]))
print("vf3  = size=%d  N=%d" % (f.vf3_entry["size"], f.N))

# --- 解 static_CH 的 6 条记录 ---
raw = f.v.read(f.v.find("static_CH", "le_strings"))
magic, ver, buckets, count = struct.unpack_from("<I H H I", raw, 0)
po = 12 + buckets * 8
CL = f.charlist


def dec(slots):
    return "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in slots)


TARGETS = ["84F287ED", "10AF1E62", "EC2D9F07", "95A79EDC", "343FEA1F", "E52F931A"]
want = {}
for t in TARGETS:
    hb = bytes.fromhex(t)
    want[bytes([hb[1], hb[0], hb[3], hb[2]])] = t

print("\n=== 6 条记录（汉化版文本）===")
for idx in range(count):
    q = struct.unpack_from("<I", raw, po + idx * 4)[0]
    b4 = raw[q:q + 4]
    if b4 not in want:
        continue
    w = q + 4
    sl = []
    while w + 2 <= len(raw):
        s = struct.unpack_from(">H", raw, w)[0]
        if s == 0:
            break
        sl.append(s)
        w += 2
    print("  %s idx=%-6d : %s" % (want[b4], idx, dec(sl)))

# --- 探测 OFFSET：找「你」在哪一格 ---
for ch in ("你", "的"):
    i = f.idx(ch)
    print("\n=== probe %s : charlist 索引 = %s ===" % (ch, i))
    if i is None:
        continue
    span = 8
    ks = list(range(i - span, i + span + 1))
    cells = [[[p[3] for p in row] for row in f.cell(f.atlas, k)] for k in ks]
    out = r"F:/sr2-cn/_probe_cn_%s.png" % ch
    sheet(cells, out)
    print("  候选格子 %d..%d -> %s" % (ks[0], ks[-1], out))
