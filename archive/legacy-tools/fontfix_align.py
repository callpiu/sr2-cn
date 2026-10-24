# -*- coding: utf-8 -*-
"""精确对齐 fnt_body_n / fnt_body_s / fnt_chinese 的 pegs 描述符与 vf3 头部。"""
import os, struct, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp, parse_vf3_header

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
NAMES = ["fnt_body_n", "fnt_body_s", "fnt_chinese"]

# pegs 描述符
descs = {}
with LightVpp(os.path.join(G, "pegs.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if nm in NAMES:
            descs[nm] = (pv.read(e), e["body"], e["size"])

# vf3
vf3s = {}
with LightVpp(os.path.join(G, "common.vpp_pc")) as cv:
    for e in cv.entries():
        nm = cv.name(e)
        if nm in NAMES and cv.ext(e) == "vf3_pc":
            vf3s[nm] = (cv.read(e), e["body"], e["size"])

# 图集 size
texs = {}
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        nm = tv.name(e)
        if nm in NAMES and not tv.ext(e):
            texs[nm] = (e["size"], e["body"])

print("=== 一、描述符前 0x40 字节逐字段对比 ===")
print("%-6s %-14s %-14s %-14s" % ("off", "fnt_body_n", "fnt_body_s", "fnt_chinese"))
for k in range(0, 0x40):
    vals = []
    for nm in NAMES:
        d = descs[nm][0]
        vals.append("%02X" % d[k] if k < len(d) else "--")
    mark = "  <<< 不同" if len(set(vals)) > 1 else ""
    print("  +%02X   %-14s %-14s %-14s%s" % (k, vals[0], vals[1], vals[2], mark))
print()

print("=== 二、描述符尾部（文件名之前）===")
for nm in NAMES:
    d = descs[nm][0]
    # 找文件名起点（'fnt_' 或 'PEG' 之后第一段可打印长串）
    i = d.find(b"fnt_")
    print("  %-14s len=%-4d 文件名@+0x%X: %r" % (nm, len(d), i, d[i:].rstrip(b"\x00").decode("latin1")))
    print("     尾部字段 +0x30..+0x%X: %s" % (i, d[0x30:i].hex(" ")))
print()

print("=== 三、vf3 头部对比 ===")
print("%-14s %-8s %-6s %-10s %-6s %-6s %-8s %-12s %-10s %-8s" %
      ("name", "size", "N", "firstasc", "W", "H", "RenderH", "CharSpacing", "KernPairs", "VertOff"))
for nm in NAMES:
    d, body, size = vf3s[nm]
    h = parse_vf3_header(d)
    print("%-14s %-8d %-6d %-10d %-6d %-6d %-8d %-12d %-10d %-8d" %
          (nm, size, h["N"], h["firstascii"], h["W"], h["H"], h["RenderH"],
           h["CharSpacing"], h["KernPairs"], h["VertOff"]))
print()

print("=== 四、图集 size ===")
for nm in NAMES:
    print("  %-14s %9d 字节  body=0x%X" % (nm, texs[nm][0], texs[nm][1]))
print()
print("  推测尺寸（DXT3 = 1 字节/像素）:")
for nm in NAMES:
    sz = texs[nm][0]
    print("    %-14s %d -> 若方形: %dx%d；若 2:1: %dx%d" %
          (nm, sz, int(sz ** 0.5), int(sz ** 0.5),
           int((sz // 2) ** 0.5) * 2, int((sz // 2) ** 0.5)))
