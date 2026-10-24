# -*- coding: utf-8 -*-
"""最终确认：字幕是否走原生 D3DX 系统字体路径。

证据链
    1. 改了 static_CH 文本（含连续索引测试串）-> 字幕无变化
    2. 改了全部 CJK 字体的度量 + 描述符 + 图集 -> 字幕无变化
       => 字幕的字形不来自任何 VPP 字体资源
    3. exe 里存在 D3DXCreateFontA + subtitle_add / subtitle_add_delayed
       => 字幕由原生 C++ 用 D3DX 字体绘制

本脚本
    找出 D3DXCreateFontA 的 IAT 槽与被调用位置，
    并检查字幕函数附近是否引用它。
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节" % len(d))
print()

# PE 段
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec, = struct.unpack_from("<H", d, coff + 2)
optsz, = struct.unpack_from("<H", d, coff + 16)
opt = coff + 20
secs = []
for i in range(nsec):
    s = opt + optsz + i * 40
    nm = d[s:s + 8].rstrip(b"\0").decode("latin1")
    vsz, va, rsz, raw = struct.unpack_from("<IIII", d, s + 8)
    secs.append((nm, va, vsz, raw, rsz))


def off2va(o):
    for nm, sva, vsz, raw, rsz in secs:
        if raw <= o < raw + rsz:
            return sva + (o - raw)
    return None


# 1) 找字幕相关函数名字符串及其邻近字符串
print("=== 字幕相关字符串及其上下文 ===")
for k in (b"subtitle_add\x00", b"subtitle_add_delayed\x00", b"tutorial_subtitles\x00"):
    i = d.find(k)
    if i < 0:
        print("  %s 未找到" % k.decode().strip("\x00"))
        continue
    print("  %-24s @0x%06X" % (k.decode().strip("\x00"), i))
    seg = d[max(0, i - 64):i + 96]
    for o in range(0, len(seg), 16):
        ch = seg[o:o + 16]
        print("     %08X  %s  |%s|" % (max(0, i - 64) + o,
                                      " ".join("%02X" % x for x in ch),
                                      "".join(chr(x) if 32 <= x < 127 else "." for x in ch)))
    print()

# 2) D3DXCreateFontA 附近
print("=== D3DXCreateFontA 附近（导入名区）===")
i = d.find(b"D3DXCreateFontA\x00")
seg = d[max(0, i - 80):i + 80]
for o in range(0, len(seg), 16):
    ch = seg[o:o + 16]
    print("  %08X  %s  |%s|" % (max(0, i - 80) + o,
                               " ".join("%02X" % x for x in ch),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in ch)))
print()

# 3) 找 d3dx9 的导入表位置（IAT 槽）
print("=== 搜索 d3dx9_39.dll 的导入目录项 ===")
i = d.find(b"d3dx9_39.dll\x00")
va = off2va(i)
print("  名称 VA = 0x%08X" % va)
pat = struct.pack("<I", va)
hits = []
j = 0
while True:
    k = d.find(pat, j)
    if k < 0:
        break
    hits.append(k)
    j = k + 1
print("  该 VA 作为 u32 出现 %d 次: %s" % (len(hits), ["0x%X" % h for h in hits[:6]]))
for h in hits[:2]:
    seg = d[max(0, h - 32):h + 32]
    print("    @0x%X:" % h)
    for o in range(0, len(seg), 16):
        ch = seg[o:o + 16]
        print("       %s  |%s|" % (" ".join("%02X" % x for x in ch),
                                   "".join(chr(x) if 32 <= x < 127 else "." for x in ch)))
print()

# 4) 字幕文本在哪（找 subtitle 函数引用的字符串）
print("=== 检查 exe 是否内嵌字幕文本 ===")
# 用汉化字表的槽位形式搜「兄弟們」
sys_path = r"F:\sr2-cn\pylibs"
import sys
sys.path.insert(0, sys_path)
from sr2lib import Vpp
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}
for w in ("兄弟們", "直升機突襲", "正要去進行交易"):
    try:
        q = b"".join(struct.pack(">H", IDX[c] + 0x20) for c in w)
        print("  %-14s 槽位形式 %s  ->  %s" % (w, q.hex(" "),
                                             "找到 @0x%X" % d.find(q) if d.find(q) >= 0 else "exe 里没有"))
    except KeyError:
        print("  %-14s 有字不在字表" % w)
