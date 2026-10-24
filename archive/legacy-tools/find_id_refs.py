# -*- coding: utf-8 -*-
"""找到引用 ACT_HELI_* 字符串 ID 的代码（即查表逻辑）。

字符串 ID 在 SR2_pc.exe 里：
  ACT_HELI_TARGETS_TEXT     @0x9E8C7C
  ACT_HELI_VAN_LIFE_TEXT    @0x9E8CFC
  ACT_HELI_KILL_CARS_START_MESSAGE @0x9E88C8

任务：找到 push offset ID 的指令，定位查表函数。
"""
import struct
import sys

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
    secs.append((nm, va, vs, rp, rs))


def off2va(o):
    for nm, va, vs, rp, rs in secs:
        if rp <= o < rp + rs:
            return base + va + (o - rp), nm
    return None, None


def va2off(va):
    r = va - base
    for nm, sva, vs, rp, rs in secs:
        if sva <= r < sva + max(vs, rs):
            return rp + (r - sva), nm
    return None, None


IDS = {}
import re
for m in re.finditer(rb"ACT_HELI_[A-Z0-9_]{3,60}", d):
    end = m.start()
    # 字符串起始
    st = end
    while st > 0 and 32 <= d[st - 1] < 127:
        st -= 1
    s = d[st:d.index(b"\x00", end)].decode()
    IDS[st] = s

print("=== exe 里的 ACT_HELI_* 字符串 (共 %d 个) ===" % len(IDS))
for o in sorted(IDS):
    va, sn = off2va(o)
    print("  0x%06X (VA 0x%08X, %s)  %s" % (o, va or 0, sn or "?", IDS[o]))
print()

# 找引用这些 VA 的指令
print("=== 引用这些字符串的代码 ===")
md = Cs(CS_ARCH_X86, CS_MODE_32)
total = 0
for o in sorted(IDS):
    va, sn = off2va(o)
    if not va:
        continue
    pat = struct.pack("<I", va)
    pos = 0
    hits = []
    while True:
        k = d.find(pat, pos)
        if k < 0:
            break
        cva, csn = off2va(k)
        hits.append((k, cva, csn))
        pos = k + 1
    if hits:
        print("  %-42s VA=0x%08X  %d 处引用" % (IDS[o], va, len(hits)))
        for k, cva, csn in hits[:4]:
            print("      代码 @文件0x%X VA=0x%X (%s)" % (k, cva or 0, csn))
            if cva:
                st = max(0, k - 24)
                for insn in md.disasm(d[st:k + 8], (cva or 0) - (k - st)):
                    mark = "  <<<" if insn.address == cva else ""
                    print("        %08X  %-18s %s %s%s" %
                          (insn.address, insn.bytes.hex(" "), insn.mnemonic, insn.op_str, mark))
        total += len(hits)
print()
print("总引用数: %d" % total)
