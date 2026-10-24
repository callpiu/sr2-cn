# -*- coding: utf-8 -*-
# 只读穷举: exe 里 fnt_chinese / 各字体名 的引用者
import os, re, struct

EXE = r"F:\sr2-cn\_backup_EXE\SR2_pc.exe.before_fontrename"
if not os.path.exists(EXE):
    EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
d = open(EXE, "rb").read()
print("exe =", EXE, len(d), "B")

# --- PE 头 ---
e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
assert d[e_lfanew:e_lfanew+4] == b"PE\0\0"
nsec = struct.unpack_from("<H", d, e_lfanew + 6)[0]
opt = e_lfanew + 24
magic = struct.unpack_from("<H", d, opt)[0]
image_base = struct.unpack_from("<I", d, opt + 28)[0] if magic == 0x10b else struct.unpack_from("<Q", d, opt + 24)[0]
print("magic=%#x image_base=%#x nsec=%d" % (magic, image_base, nsec))
sects = []
sh = opt + (224 if magic == 0x10b else 240)
for i in range(nsec):
    o = sh + i * 40
    nm = d[o:o+8].rstrip(b"\0").decode("latin1")
    vsz, va, rsz, ro = struct.unpack_from("<IIII", d, o + 8)
    sects.append((nm, va, vsz, ro, rsz))
    print("  %-9s VA=%#010x VSz=%#x  Raw=%#010x RSz=%#x" % (nm, va, vsz, ro, rsz))

def va2off(va):
    for nm, sva, vsz, ro, rsz in sects:
        if sva <= va < sva + max(vsz, rsz):
            return ro + (va - sva)
    return None

NAMES = ["jap", "fnt_chinese", "fnt_korea", "fnt_cz", "fnt_cz_s",
         "fnt_body_n", "fnt_body_s", "fnt_bodyital_n", "fnt_bodyital_s",
         "fnt_head_n", "fnt_head_s", "ug-debug", "debug",
         "thin", "thin_overlay", "header_n", "header_n_overlay",
         "bodyital_overlay", "font_hudsmall"]

print("\n=== 字符串位置 ===")
locs = {}
for nm in NAMES:
    pat = nm.encode() + b"\0"
    i = d.find(pat)
    if i < 0:
        print("  %-18s NOT FOUND" % nm); continue
    # 反查 VA
    va = None
    for snm, sva, vsz, ro, rsz in sects:
        if ro <= i < ro + rsz:
            va = sva + (i - ro); break
    locs[nm] = (i, va)
    print("  %-18s off=%#010x VA=%s" % (nm, i, ("%#010x" % va) if va else "?"))

print("\n=== 引用计数 (4字节 LE VA, 在 .text 里搜) ===")
text = [(nm, va, vsz, ro, rsz) for nm, va, vsz, ro, rsz in sects if nm == ".text"]
for nm, (off, va) in locs.items():
    if va is None: continue
    target = image_base + va
    pat = struct.pack("<I", target)
    refs = [m.start() for m in re.finditer(re.escape(pat), d)]
    print("  %-18s VA=%#010x  引用=%d" % (nm, target, len(refs)))
    for r in refs[:6]:
        rva = None
        for snm, sva, vsz, ro, rsz in sects:
            if ro <= r < ro + rsz:
                rva = sva + (r - ro); break
        print("      @file %#010x  VA %#010x" % (r, (image_base + rva) if rva else 0))
