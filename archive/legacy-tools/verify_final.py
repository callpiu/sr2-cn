# -*- coding: utf-8 -*-
"""最终校验 sr2_subfix.dll：结构 + 导出 + 代码内容合理性。"""
import struct
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"F:\sr2-cn\asi\sr2_subfix.dll"
d = open(path, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
entry, = struct.unpack_from("<I", d, opt + 16)
base, = struct.unpack_from("<I", d, opt + 28)
sizeimg, = struct.unpack_from("<I", d, opt + 56)
ndd, = struct.unpack_from("<I", d, opt + 92)
exp_rva, exp_size = struct.unpack_from("<II", d, opt + 96)
imp_rva, imp_size = struct.unpack_from("<II", d, opt + 104)
rel_rva, rel_size = struct.unpack_from("<II", d, opt + 168)

secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs, fl))

print("=" * 70)
print("sr2_subfix.dll 最终校验")
print("=" * 70)
print("  大小        : %d 字节" % len(d))
print("  机器        : 0x%04X (%s)" % (mach, "i386 ✓" if mach == 0x14C else "✗"))
print("  类型        : %s" % ("DLL ✓" if chars & 0x2000 else "✗ 不是 DLL"))
print("  入口点      : 0x%X %s" % (entry, "✓" if entry else "✗ 无入口"))
print("  ImageBase   : 0x%08X" % base)
print("  SizeOfImage : 0x%X" % sizeimg)
print("  导入表      : RVA=0x%X size=%d %s" % (imp_rva, imp_size,
      "✓ 零导入（用 PEB）" if imp_rva == 0 else ""))
print("  导出表      : RVA=0x%X size=%d" % (exp_rva, exp_size))
print("  重定位表    : RVA=0x%X size=%d" % (rel_rva, rel_size))
print()


def rva2off(rva):
    for nm, va, vs, rp, rs, fl in secs:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return None


# 导出
o = rva2off(exp_rva)
# IMAGE_EXPORT_DIRECTORY: +12 Name, +16 Base, +20 NumberOfFunctions, +24 NumberOfNames,
#                         +28 AddressOfFunctions, +32 AddressOfNames, +36 AddressOfNameOrdinals
dllname_rva, = struct.unpack_from("<I", d, o + 12)
nfun, = struct.unpack_from("<I", d, o + 20)
nnam, = struct.unpack_from("<I", d, o + 24)
addr_rva, = struct.unpack_from("<I", d, o + 28)
nam_rva, = struct.unpack_from("<I", d, o + 32)
ord_rva, = struct.unpack_from("<I", d, o + 36)
print("  导出 DLL 名 : %s" % d[rva2off(dllname_rva):d.index(b"\x00", rva2off(dllname_rva))].decode())
print("  导出函数    :")
for i in range(nnam):
    no = rva2off(nam_rva + 4 * i)
    nr, = struct.unpack_from("<I", d, no)
    so = rva2off(nr)
    end = d.index(b"\x00", so)
    name = d[so:end].decode()
    oo = rva2off(ord_rva + 2 * i)
    od, = struct.unpack_from("<H", d, oo)
    fo = rva2off(addr_rva + 4 * od)
    frva, = struct.unpack_from("<I", d, fo)
    print("    %-24s ord=%-3d RVA=0x%-6X" % (name, od, frva))
print()

# 检查 .text 开头几条指令（入口）
toff = rva2off(entry)
print("  入口点代码（前 32 字节）:")
for k in range(0, 32, 8):
    chunk = d[toff + k:toff + k + 8]
    print("    +%02X  %s" % (k, " ".join("%02X" % x for x in chunk)))
print()

# 检查在 .rdata 里能不能找到目标字符串
print("  .rdata 里的目标串（UTF-16LE）:")
KEY1 = "使發光彈借歷復使發俱誘".encode("utf-16-le")
KEY2 = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋".encode("utf-16-le")
GOOD1 = "Your homies need your protection".encode("utf-16-le")
GOOD2 = "Protect your homies from attackers".encode("utf-16-le")
for label, k in (("bad1", KEY1), ("bad2", KEY2), ("good1", GOOD1), ("good2", GOOD2)):
    i = d.find(k)
    print("    %-6s %s" % (label, "✓ @0x%X" % i if i >= 0 else "✗ 未找到"))

print()
print("=" * 70)
print("结论: %s" % ("DLL 结构完整，可以注入 ✓" if mach == 0x14C and entry and (chars & 0x2000)
                 and d.find(KEY2) >= 0 and d.find(GOOD2) >= 0 else "★ 有问题"))
