# -*- coding: utf-8 -*-
"""搜索游戏里对 D3DXCreateFontA IAT 槽（VA 0x00DB8418）的所有引用。"""
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(EXE, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs))

IAT_VA = 0x00DB8418
pat = struct.pack("<I", IAT_VA)

print("=== 所有对 IAT VA 0x%08X 的引用 ===" % IAT_VA)
hits = []
pos = 0
while True:
    k = d.find(pat, pos)
    if k < 0:
        break
    va = None
    secname = "?"
    for nm, sva, vs, rp, rs in secs:
        if rp and rp <= k < rp + rs:
            va = sva + (k - rp)
            secname = nm
            break
    hits.append((k, va, secname))
    pos = k + 1

print("  找到 %d 处" % len(hits))
md = Cs(CS_ARCH_X86, CS_MODE_32)
for k, va, sn in hits[:12]:
    print()
    print("  文件 0x%X  VA 0x%X (节 %s)" % (k, va if va else 0, sn))
    if va is None:
        continue
    # 反汇编前 32 字节
    start = max(0, k - 32)
    base = va - (k - start)
    print("    前置指令:")
    for insn in md.disasm(d[start:k], base):
        print("      %08X  %-20s %s %s" % (insn.address, insn.bytes.hex(" "),
                                            insn.mnemonic, insn.op_str))
    print("    >>> 数据引用 (VA 0x%08X)" % va)
    for insn in md.disasm(d[k:k + 16], va):
        print("      %08X  %-20s %s %s" % (insn.address, insn.bytes.hex(" "),
                                            insn.mnemonic, insn.op_str))
