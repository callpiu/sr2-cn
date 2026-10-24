# -*- coding: utf-8 -*-
"""验证生成的 DLL 是一个结构正确的 PE32。"""
import struct
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"F:\sr2-cn\asi\sr2_subfix.dll"
d = open(path, "rb").read()
print("文件: %s (%d 字节)" % (path, len(d)))
print("DOS 头: %r  e_lfanew=0x%X" % (d[:2], struct.unpack_from("<I", d, 0x3C)[0]))
e = struct.unpack_from("<I", d, 0x3C)[0]
print("PE 签名: %r" % d[e:e + 4])
mach, nsec, tds, psym, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
print("machine=0x%04X 节数=%d optsize=%d characteristics=0x%04X (%s)" %
      (mach, nsec, optsz, chars,
       "DLL" if chars & 0x2000 else "-"))
opt = e + 24
magic, = struct.unpack_from("<H", d, opt)
print("Optional magic=0x%X (%s)" % (magic, "PE32" if magic == 0x10B else "?"))
entry, = struct.unpack_from("<I", d, opt + 16)
base, = struct.unpack_from("<I", d, opt + 28)
salign, = struct.unpack_from("<I", d, opt + 32)
falign, = struct.unpack_from("<I", d, opt + 36)
sizeimg, = struct.unpack_from("<I", d, opt + 56)
sizehdr, = struct.unpack_from("<I", d, opt + 60)
subsys, = struct.unpack_from("<H", d, opt + 68)
ndd, = struct.unpack_from("<I", d, opt + 92)
print("EntryPoint=0x%X ImageBase=0x%X SectionAlign=0x%X FileAlign=0x%X" %
      (entry, base, salign, falign))
print("SizeOfImage=0x%X SizeOfHeaders=0x%X Subsystem=%d NumDataDir=%d" %
      (sizeimg, sizehdr, subsys, ndd))
exp_rva, exp_size = struct.unpack_from("<II", d, opt + 96)
print("导出目录: RVA=0x%X size=%d" % (exp_rva, exp_size))
print()

print("=== 节表 ===")
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs, fl))
    print("  %-12s VA=0x%-6X vsize=%-6d raw=0x%-6X rsize=%-6d flags=0x%08X" %
          (nm, va, vs, rp, rs, fl))
print()

# 校验每节数据在文件内
ok = True
for nm, va, vs, rp, rs, fl in secs:
    if rs and rp + rs > len(d):
        print("  ★ %s 数据越界: raw 0x%X + %d > %d" % (nm, rp, rs, len(d)))
        ok = False
print("节数据边界: %s" % ("OK" if ok else "★ 有问题"))

# 导出表解析
def rva2off(rva):
    for nm, va, vs, rp, rs, fl in secs:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return None

if exp_rva:
    o = rva2off(exp_rva)
    if o is not None:
        b, nfun, nnam = struct.unpack_from("<III", d, o + 12)
        addr_rva, nam_rva, ord_rva = struct.unpack_from("<III", d, o + 28)
        dllname_rva, = struct.unpack_from("<I", d, o + 12)
        print()
        print("=== 导出表 ===")
        print("  Base=%d NumberOfFunctions=%d NumberOfNames=%d" % (b, nfun, nnam))
        for i in range(nnam):
            no = rva2off(nam_rva + 4 * i) if nam_rva else None
            if no is None:
                continue
            nr, = struct.unpack_from("<I", d, no)
            so = rva2off(nr)
            if so is None:
                continue
            end = d.index(b"\x00", so)
            name = d[so:end].decode("latin1")
            # 序数
            oo = rva2off(ord_rva + 2 * i)
            od, = struct.unpack_from("<H", d, oo)
            fo = rva2off(addr_rva + 4 * od)
            frva, = struct.unpack_from("<I", d, fo)
            print("    %-20s ord=%-3d RVA=0x%X" % (name, od, frva))
    else:
        print("  ★ 导出表 RVA 无法映射到文件偏移")
print()
print("结论: %s" % ("PE32 DLL 结构正确 ✓" if ok and magic == 0x10B else "★ 结构有问题"))
