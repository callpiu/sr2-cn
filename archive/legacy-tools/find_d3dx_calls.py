# -*- coding: utf-8 -*-
"""分析 SR2_pc.exe 如何调用 D3DXCreateFontA。

关键问题
    hook 装上了但从未触发 -> 游戏是否真的调用它？怎么调用的？
"""
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(EXE, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
imp_rva, imp_size = struct.unpack_from("<II", d, opt + 104)
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs))


def r2o(rva):
    for nm, va, vs, rp, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va), nm
    return None, None


# 找 D3DXCreateFontA 的 IAT 槽
off, _ = r2o(imp_rva)
i = 0
d3dx_iat = None
while True:
    o = off + i * 20
    oft, tds, fc, name_rva, ft = struct.unpack_from("<IIIII", d, o)
    if name_rva == 0:
        break
    no, _ = r2o(name_rva)
    end = d.index(b"\x00", no)
    dll = d[no:end].decode()
    if "d3dx9" in dll.lower():
        # 遍历 thunk
        thunk_rva = oft if oft else ft
        to, _ = r2o(thunk_rva)
        k = 0
        while True:
            v, = struct.unpack_from("<I", d, to + k * 4)
            if v == 0:
                break
            if not (v & 0x80000000):
                fo, _ = r2o(v)
                fe = d.index(b"\x00", fo + 2)
                fn = d[fo + 2:fe].decode()
                if fn == "D3DXCreateFontA":
                    d3dx_iat = ft + k * 4
                    print("D3DXCreateFontA IAT VA = 0x%08X" % (0x400000 + d3dx_iat))
            k += 1
    i += 1

if not d3dx_iat:
    print("★ 未找到 IAT 槽")
    sys.exit(0)

# 在 .text 里搜索对 IAT 槽的直接引用 (FF 15 xx xx xx xx = call dword ptr [addr])
iat_va = 0x400000 + d3dx_iat
pat = struct.pack("<I", iat_va)
print()
print("=== 搜索 'call dword ptr [D3DXCreateFontA]' (FF 15) ===")
hits = []
pos = 0
while True:
    k = d.find(pat, pos)
    if k < 0:
        break
    # 检查前两字节是否 FF 15
    if k >= 2 and d[k - 2] == 0xFF and d[k - 1] == 0x15:
        va = None
        for nm, sva, vs, rp, rs in secs:
            if rp and rp <= k < rp + rs:
                va = sva + (k - rp)
                break
        hits.append((k, va))
    pos = k + 1

print("  找到 %d 处调用点" % len(hits))
md = Cs(CS_ARCH_X86, CS_MODE_32)
for k, va in hits:
    print("  文件偏移 0x%X  VA 0x%X" % (k, va if va else 0))
    # 反汇编附近
    start = max(0, k - 40)
    for insn in md.disasm(d[start:k + 12], 0x400000 + (va - (k - start) if va else 0)):
        mark = "  <<< 调用" if insn.address == (0x400000 + va if va else -1) else ""
        print("      %08X  %-20s %s %s%s" % (insn.address, insn.bytes.hex(" "),
                                              insn.mnemonic, insn.op_str, mark))
    print()
