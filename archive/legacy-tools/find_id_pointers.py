# -*- coding: utf-8 -*-
"""找引用 ACT_HELI_* 字符串 ID 的指针表，以及读取它的代码。"""
import re
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(EXE, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
base, = struct.unpack_from("<I", d, opt + 28)
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs, fl))


def off2va(o):
    for nm, va, vs, rp, rs, fl in secs:
        if rp and rp <= o < rp + rs:
            return base + va + (o - rp), nm
    return None, None


def va2off(va):
    r = va - base
    for nm, sva, vs, rp, rs, fl in secs:
        if sva <= r < sva + max(vs, rs):
            return rp + (r - sva), nm
    return None, None


IDS = {}
for m in re.finditer(rb"ACT_HELI_[A-Z0-9_]{3,60}", d):
    end = m.start()
    st = end
    while st > 0 and 32 <= d[st - 1] < 127:
        st -= 1
    IDS[st] = d[st:d.index(b"\x00", end)].decode()

vas = {}
for o, s in IDS.items():
    va, sn = off2va(o)
    if va:
        vas[va] = s

print("=== 搜索指向这些字符串的指针（4 字节 LE）===")
allrefs = {}
for va, s in sorted(vas.items()):
    pat = struct.pack("<I", va)
    pos = 0
    while True:
        k = d.find(pat, pos)
        if k < 0:
            break
        rva, rsn = off2va(k)
        allrefs.setdefault(k, []).append(s)
        pos = k + 1

if allrefs:
    print("  找到 %d 个指针位置:" % len(allrefs))
    for k in sorted(allrefs)[:40]:
        rva, rsn = off2va(k)
        print("    0x%06X (VA 0x%08X, %s)  ->  %s" %
              (k, rva or 0, rsn or "?", ", ".join(allrefs[k][:3])))
else:
    print("  ✗ 没有找到指针（字符串可能只被间接引用）")

print()
print("=== .rdata 里 0x00DE8800..0x00DE8900 区域（看是否有 ID 表）===")
o, _ = va2off(0x00DE8800)
if o:
    for x in range(0, 0x100, 16):
        ch = d[o + x:o + x + 16]
        print("  VA %08X  %s  |%s|" % (0x00DE8800 + x,
              " ".join("%02X" % c for c in ch),
              "".join(chr(c) if 32 <= c < 127 else "." for c in ch)))

print()
print("=== 搜索引用 0x00DE8xxx 区域的指令（mov/push 立即数）===")
md = Cs(CS_ARCH_X86, CS_MODE_32)
lo, hi = 0x00DE8000, 0x00DEB000
ncode = 0
# 扫描 .text 找形如 B8..BF/B8 imm32 或 68 imm32 的指令，imm 落在 ID 区
textoff = None
for nm, va, vs, rp, rs, fl in secs:
    if nm == ".text" and rp:
        textoff, textva, textsz = rp, va + base, rs
        break
if textoff:
    i = 0
    while i < textsz - 5:
        op = d[textoff + i]
        imm = None
        if op == 0x68:                                  # push imm32
            imm = struct.unpack_from("<I", d, textoff + i + 1)[0]
        elif 0xB8 <= op <= 0xBF:                        # mov r32, imm32
            imm = struct.unpack_from("<I", d, textoff + i + 1)[0]
        if imm is not None and lo <= imm < hi:
            va0 = textva + i
            print("  代码 VA 0x%08X  %-18s -> 0x%08X" %
                  (va0, d[textoff + i:textoff + i + 5].hex(" "), imm))
            ncode += 1
            if ncode > 30:
                break
        i += 1
print("  命中 %d" % ncode)
