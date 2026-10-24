# -*- coding: utf-8 -*-
"""在 SR2_pc.exe 数据段定位字表全局变量 0x02528B2C/0x02528B30，
并检查附近是否有第二个 (ptr,count) 字表结构（common 字体用）。"""
import struct, sys, os

CAND = [r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe",
        r"F:\sr2-cn\SR2_pc.exe.orig",
        r"F:\sr2-cn\SR2_pc.exe.before_data"]
path = next((p for p in CAND if os.path.exists(p)), None)
print("exe =", path)
buf = open(path, "rb").read()
print("size = 0x%X" % len(buf))

# --- PE 解析 ---
e_lfanew = struct.unpack_from("<I", buf, 0x3C)[0]
assert buf[e_lfanew:e_lfanew+4] == b"PE\0\0"
coff = e_lfanew + 4
nsec = struct.unpack_from("<H", buf, coff+2)[0]
optsz = struct.unpack_from("<H", buf, coff+16)[0]
opt = coff + 20
magic = struct.unpack_from("<H", buf, opt)[0]
pe32p = (magic == 0x20B)
imgbase = struct.unpack_from("<Q" if pe32p else "<I", buf, opt+24)[0]
print("PE32+" if pe32p else "PE32", " ImageBase=0x%X" % imgbase, " sections=%d" % nsec)

secs = []
saddr = opt + optsz
for i in range(nsec):
    o = saddr + i*40
    name = buf[o:o+8].rstrip(b"\0").decode("latin1")
    vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", buf, o+8)
    secs.append((name, vaddr, vsize, raddr, rsize))
    print("  %-8s VA=0x%08X VS=0x%08X RAW=0x%08X RS=0x%08X" % (name, vaddr, vsize, raddr, rsize))

def va2off(va):
    for name, vaddr, vsize, raddr, rsize in secs:
        if vaddr <= va < vaddr + max(vsize, rsize):
            return raddr + (va - vaddr)
    return None

# --- 目标区转储 ---
LO, HI = 0x02528000, 0x02529000
o0, o1 = va2off(LO), va2off(HI)
print("\n目标区 VA 0x%08X-0x%08X -> 文件偏移 0x%X-0x%X" % (LO, HI, o0, o1))
if o0 is None or o1 is None:
    sys.exit("VA 不在任何节内")

print("\n=== 0x02528B2C / 0x02528B30 处当前值（exe 静态初值）===")
for va in (0x02528B2C, 0x02528B30):
    off = va2off(va)
    print("  VA 0x%08X -> 0x%08X  u32=0x%08X" % (va, off, struct.unpack_from("<I", buf, off)[0]))

print("\n=== 全数据段扫描: 相邻 (ptr, count) 且 count 在 500..6000 ===")
hits = []
for name, vaddr, vsize, raddr, rsize in secs:
    if name not in (".data", ".rdata", ".bss", "DATA"): continue
    if rsize == 0: continue
    end = min(raddr + rsize, len(buf))
    for off in range(raddr, end - 8, 4):
        p, c = struct.unpack_from("<II", buf, off)
        # 指针应指向镜像内某处（imagebase..imagebase+0x1000000），count 合理
        if 500 <= c <= 6000 and imgbase <= p < imgbase + 0x2000000:
            va = vaddr + (off - raddr)
            hits.append((va, p, c))
print("  候选 (ptr,count) 共 %d 个" % len(hits))
for va, p, c in hits:
    star = ""
    if va in (0x02528B2C,): star = "   <<<< 已知 CHARLIST_PTR"
    print("    VA 0x%08X: ptr=0x%08X (RVA 0x%X)  count=%d%s" % (va, p, p-imgbase, c, star))

print("\n=== 全文件搜索 u32 常量 2838 / 2795 / 2803 ===")
for target in (2838, 2795, 2803, 2839, 2794):
    tb = struct.pack("<I", target)
    pos = []
    st = 0
    while True:
        i = buf.find(tb, st)
        if i < 0: break
        pos.append(i); st = i + 1
        if len(pos) > 40: break
    print("  %5d (0x%04X): %d 处  文件偏移 %s" % (target, target, len(pos), [hex(x) for x in pos[:12]]))
