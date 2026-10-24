"""精确定位字体名与别名表在 SR2_pc.exe 里的真实位置。"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节, MZ=%s" % (len(d), d[:2]))

# PE 段表
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec, = struct.unpack_from("<H", d, coff + 2)
optsz, = struct.unpack_from("<H", d, coff + 16)
opt = coff + 20
magic, = struct.unpack_from("<H", d, opt)
print("PE@0x%X nsec=%d optsz=%d magic=0x%X" % (e, nsec, optsz, magic))
secs = []
for i in range(nsec):
    s = opt + optsz + i * 40
    nm = d[s:s + 8].rstrip(b"\0").decode("latin1")
    vsz, va, rsz, raw = struct.unpack_from("<IIII", d, s + 8)
    secs.append((nm, va, vsz, raw, rsz))
    print("  %-8s VA=%08X vsz=%08X raw=%08X rsz=%08X" % (nm, va, vsz, raw, rsz))


def va2off(va):
    for nm, sva, vsz, raw, rsz in secs:
        if sva <= va < sva + max(vsz, rsz):
            return raw + (va - sva)
    return None


print()
print("=== 关键字符串的 VA 与文件偏移 ===")
for name in (b"fnt_body_n", b"fnt_body_s", b"thin_overlay", b"thin\x00",
             b"header_n", b"fnt_chinese", b"jap\x00"):
    i = d.find(name)
    if i < 0:
        print("  %-16s 未找到" % name.decode("latin1"))
        continue
    va = None
    for nm, sva, vsz, raw, rsz in secs:
        if raw <= i < raw + rsz:
            va = sva + (i - raw)
            break
    print("  %-16s 文件 0x%08X  VA 0x%08X" % (name.decode("latin1"), i, va if va else 0))

print()
print("=== thin_overlay 附近的字节（文件偏移）===")
i = d.find(b"thin_overlay")
seg = d[i - 32:i + 64]
for k in range(0, len(seg), 16):
    print("  %08X  %s  |%s|" % (i - 32 + k,
                               " ".join("%02X" % x for x in seg[k:k + 16]),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in seg[k:k + 16])))
print()

# 找指向这些字符串的指针（小端 u32）
print("=== 谁引用了 fnt_body_n / fnt_body_s（找 u32 指针）===")
for name in (b"fnt_body_n", b"fnt_body_s", b"fnt_chinese"):
    i = d.find(name)
    va = None
    for nm, sva, vsz, raw, rsz in secs:
        if raw <= i < raw + rsz:
            va = sva + (i - raw)
            break
    if va is None:
        continue
    pat = struct.pack("<I", va)
    hits = []
    j = 0
    while True:
        k = d.find(pat, j)
        if k < 0:
            break
        hits.append(k)
        j = k + 1
    print("  %-16s VA=0x%08X  被引用 %d 次: %s" %
          (name.decode(), va, len(hits), ["0x%X" % h for h in hits[:8]]))
