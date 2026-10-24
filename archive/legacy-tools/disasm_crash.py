# -*- coding: utf-8 -*-
"""反汇编 dinput8.dll 崩溃点（RVA 0x14FC）附近。"""
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

sys.path.insert(0, r"F:\sr2-cn")
from link_pe2 import parse_coff

DLL = r"F:\sr2-cn\asi\dinput8.dll"
OBJ = r"F:\sr2-cn\asi\dinput8.obj"
CRASH = 0x14FC

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
base, = struct.unpack_from("<I", d, opt + 28)
entry, = struct.unpack_from("<I", d, opt + 16)
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


print("ImageBase = 0x%08X   入口点 RVA = 0x%X" % (base, entry))
off, sn = r2o(CRASH)
print("崩溃 RVA = 0x%X -> 文件偏移 0x%X (节 %s)" % (CRASH, off, sn))
print()

md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=" * 74)
print("崩溃点附近（前 64 字节）")
print("=" * 74)
for i in md.disasm(d[off - 64:off + 48], base + CRASH - 64):
    mark = "   <<<<<< 崩溃" if i.address == base + CRASH else ""
    print("  %08X  %-22s %-8s %s%s" % (i.address, i.bytes.hex(" "),
                                        i.mnemonic, i.op_str, mark))
print()

eo, _ = r2o(entry)
print("=" * 74)
print("入口点 DllMain (RVA 0x%X)" % entry)
print("=" * 74)
for i in md.disasm(d[eo:eo + 128], base + entry):
    print("  %08X  %-22s %-8s %s" % (i.address, i.bytes.hex(" "), i.mnemonic, i.op_str))
print()

print("=" * 74)
print("函数列表（用 obj 符号表）")
print("=" * 74)
secs2, syms = parse_coff(open(OBJ, "rb").read())
merged = {}
order = []
secmap = {}
for s in secs2:
    k = s["name"]
    if k not in merged:
        merged[k] = bytearray()
        order.append(k)
    m = merged[k]
    align = 16 if (s["flags"] & 0x20) else 8
    m += b"\x00" * ((-len(m)) % align)
    o2 = len(m)
    m += s["raw"]
    secmap[s["idx"]] = (k, o2)
va = 0x1000
rvas = {}
for k in order:
    rvas[k] = va
    va += (len(merged[k]) + 0xFFF) & ~0xFFF
funcs = []
for sy in syms:
    if sy is None or sy["sec"] <= 0 or sy["type"] != 0x20:
        continue
    k, b = secmap[sy["sec"]]
    funcs.append((rvas[k] + b + sy["value"], sy["name"]))
funcs.sort()
for j, (rva, nm) in enumerate(funcs):
    nxt = funcs[j + 1][0] if j + 1 < len(funcs) else 0x7FFFFFFF
    mark = "   <<< 崩溃在此函数内" if rva <= CRASH < nxt else ""
    print("  0x%05X  %-46s%s" % (rva, nm, mark))
