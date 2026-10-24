# -*- coding: utf-8 -*-
"""确认 D3DXCreateFontA 的调用点，并检查游戏如何用槽位查询字符。

关键推理
    D3DXCreateFontA(face, ...) 只接受【系统 TrueType 字体名】。
    如果字幕用它，那么字幕的文字必须由【系统字体】渲染。
    但游戏内部存的是【槽位】(slot)，要显示必须先用 charlist 换成 Unicode。
    -> 若转换正确，D3DX 用系统字体渲染中文是没问题的（系统有 SimSun 等）。
    -> 乱码说明：转换出来的 Unicode 不对，或者字体不支持 CJK 而回退。

本脚本
    1. 找 D3DXCreateFontA 的 IAT 引用（谁调用它）
    2. 找 cc_list / num_cchars 的引用（compress_char 相关）
    3. 找「槽位 -> Unicode」的反向查询函数
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节" % len(d))

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


def va2off(va):
    for nm, sva, vsz, raw, rsz in secs:
        if sva <= va < sva + max(vsz, rsz):
            return raw + (va - sva)
    return None


# 1) D3DXCreateFontA 的 IAT 槽
i = d.find(b"D3DXCreateFontA\x00")
va = off2va(i)
print("D3DXCreateFontA 字符串 VA = 0x%08X" % va)
# 找 IAT：指向该字符串的 u32
pat = struct.pack("<I", va)
hits = []
j = 0
while True:
    k = d.find(pat, j)
    if k < 0:
        break
    hits.append(k)
    j = k + 1
print("  该 VA 作为 u32 出现 %d 次: %s" % (len(hits), ["0x%X" % h for h in hits[:10]]))
for h in hits[:6]:
    print("    @0x%X (段 %s)" % (h, next((nm for nm, sva, vsz, raw, rsz in secs
                                          if raw <= h < raw + rsz), "?")))

# 2) 全局变量：cc_list @ 0x02528B2C, num_cchars @ 0x02528B30
print()
print("=== cc_list / num_cchars ===")
for name, gva in (("cc_list", 0x02528B2C), ("num_cchars", 0x02528B30)):
    pat = struct.pack("<I", gva)
    hits = []
    j = 0
    while True:
        k = d.find(pat, j)
        if k < 0:
            break
        hits.append(k)
        j = k + 1
    print("  %-12s VA=0x%08X 被引用 %d 次: %s" % (name, gva, len(hits), ["0x%X" % h for h in hits[:10]]))
    for h in hits[:4]:
        o = va2off(gva)
        print("      @0x%X 附近代码: %s" % (h, d[max(0, h - 8):h + 12].hex(" ")))

# 3) 找 d3dx9_39.dll 导入表项
print()
print("=== d3dx9_39.dll 导入表 ===")
i = d.find(b"d3dx9_39.dll\x00")
print("  字符串 @0x%X VA=0x%08X" % (i, off2va(i)))
seg = d[i - 0x200:i + 0x200]
names = [s.decode("latin1") for s in seg.split(b"\x00") if 6 <= len(s) <= 40 and s.isascii()]
print("  附近导入函数名: %s" % ", ".join(n for n in names if n.startswith("D3DX") or n.startswith("d3dx")))
