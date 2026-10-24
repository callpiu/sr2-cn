# -*- coding: utf-8 -*-
"""彻底搜索：游戏到底怎么用 D3DXCreateFontA？"""
import struct

EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(EXE, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
base, = struct.unpack_from("<I", d, opt + 28)
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


print("ImageBase = 0x%08X" % base)
print("导入表 RVA = 0x%X size = %d" % (imp_rva, imp_size))
print()

off, sn = r2o(imp_rva)
print("=== 导入描述符逐项 (文件偏移 0x%X, 节 %s) ===" % (off, sn))
i = 0
while True:
    o = off + i * 20
    oft, tds, fc, name_rva, ft = struct.unpack_from("<IIIII", d, o)
    if name_rva == 0:
        break
    no, _ = r2o(name_rva)
    end = d.index(b"\x00", no)
    dll = d[no:end].decode()
    print("  [%d] %-18s OFT=0x%-8X FT=0x%-8X" % (i, dll, oft, ft))
    if "d3dx" in dll.lower():
        # 完整列出 thunk 和 IAT
        thunk_rva = oft if oft else ft
        to, _ = r2o(thunk_rva)
        io_, _ = r2o(ft)
        k = 0
        while True:
            v, = struct.unpack_from("<I", d, to + k * 4)
            iv, = struct.unpack_from("<I", d, io_ + k * 4)
            if v == 0 and iv == 0:
                break
            nm2 = "?"
            if v and not (v & 0x80000000):
                fo, _ = r2o(v)
                fe = d.index(b"\x00", fo + 2)
                nm2 = d[fo + 2:fe].decode()
            print("        k=%d  OFT=0x%08X  IAT_VA=0x%08X  %s" %
                  (k, v, base + ft + k * 4, nm2))
            if not nm2 or nm2 == "?":
                break
            k += 1
            if k > 8:
                break
    i += 1
print()

# 直接找所有 0xDB84xx 形式的地址
print("=== 搜索所有 0x00DB84xx 形式的 u32 ===")
found = {}
for target in range(0x00DB8400, 0x00DB8430, 4):
    pat = struct.pack("<I", target)
    pos = 0
    cnt = 0
    while True:
        k = d.find(pat, pos)
        if k < 0:
            break
        cnt += 1
        pos = k + 1
    if cnt:
        found[target] = cnt
        print("  0x%08X: %d 处" % (target, cnt))
if not found:
    print("  整个 exe 里没有任何 0x00DB84xx 地址引用")
