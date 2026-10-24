"""在 SR2_pc.exe 里找字体别名表（thin_overlay -> fnt_body_n 等）。

交接文档给的地址 0x11d612 在【无 LAA 的原版 exe】上可能对应不同文件偏移。
本脚本做两件事：
  1. 对多个 exe 版本，搜索「thin_overlay 的 VA」作为 u32 出现在哪些地方
  2. 搜索「别名字符串连续排列」的特征块（别名表可能在 .rdata）
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
EXES = ["SR2_pc.exe", "sr2_pc_unpatched.exe", "SR2_pc.exe.bak"]

PAIRS = [
    ("thin", 0x9E1060), ("thin_overlay", 0x9E1068),
    ("header_n", 0x9E1078), ("header_n_overlay", 0x9E1088),
    ("bodyital_overlay", 0x9E1098), ("debug", 0x9E1058),
]

for fn in EXES:
    p = os.path.join(G, fn)
    if not os.path.exists(p):
        print("=== %s 不存在 ===" % fn)
        continue
    d = open(p, "rb").read()
    print("=== %s (%d 字节) ===" % (fn, len(d)))
    # 找 PE 段
    e = struct.unpack_from("<I", d, 0x3C)[0]
    coff = e + 4
    nsec, = struct.unpack_from("<H", d, coff + 2)
    optsz, = struct.unpack_from("<H", d, coff + 16)
    opt = coff + 20
    secs = []
    for i in range(nsec):
        s = opt + optsz + i * 40
        nm = d[s:s + 8].rstrip(b"\0").decode("latin1")
        vsz, va, rsz, raw = struct.unpack_from("<IIII", d, s + 8)
        secs.append((nm, va, vsz, raw, rsz))

    def off2va(o):
        for nm, sva, vsz, raw, rsz in secs:
            if raw <= o < raw + rsz:
                return sva + (o - raw)
        return None

    # 找别名字符串
    for name, _ in PAIRS:
        i = d.find(name.encode() + b"\x00")
        if i < 0:
            print("    %-20s 未找到" % name)
            continue
        va = off2va(i)
        print("    %-20s 文件 0x%08X  VA 0x%08X" % (name, i, va if va else 0))
    # 搜「thin_overlay」VA 作为 u32 的所有出现
    i = d.find(b"thin_overlay\x00")
    if i >= 0:
        va = off2va(i)
        pat = struct.pack("<I", va)
        hits = []
        j = 0
        while True:
            k = d.find(pat, j)
            if k < 0:
                break
            hits.append(k)
            j = k + 1
        print("    → thin_overlay VA=0x%08X 作为 u32 出现 %d 次: %s" %
              (va, len(hits), ["0x%X" % h for h in hits[:10]]))
        # 打印每个命中点附近
        for h in hits[:4]:
            seg = d[max(0, h - 16):h + 48]
            print("      @0x%X: %s" % (h, " ".join("%02X" % x for x in seg)))
    print()
