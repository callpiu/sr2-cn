"""读 pegs 描述符 + vf3 头部，搞清 fnt_body_n/s 与 fnt_chinese 的结构差异。"""
import os, struct, sys

sys.path.insert(0, r"F:\sr2-cn")
exec(open(r"F:\sr2-cn\fontfix_inventory.py").read().split("for fn in (")[0])

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- pegs 描述符 ----
pv = LightVpp(os.path.join(G, "pegs.vpp_pc"))
print("=== pegs.vpp_pc 里的字体描述符（完整 hex）===")
for e in pv.entries():
    nm = pv.name(e)
    if nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_head_n"):
        d = pv.read(e)
        print("  %s (%d 字节, body=0x%X):" % (nm, len(d), e["body"]))
        for k in range(0, len(d), 16):
            print("     +%02X  %s  |%s|" % (k,
                  " ".join("%02X" % x for x in d[k:k + 16]),
                  "".join(chr(x) if 32 <= x < 127 else "." for x in d[k:k + 16])))
        print()
pv.close()

# ---- vf3 头部 ----
print("=== common.vpp_pc 里 vf3 的头部字段 ===")
def vf3info(path, want):
    v = LightVpp(path)
    out = {}
    for e in v.entries():
        nm = v.name(e)
        ex = v.ext(e)
        if nm in want and ex == "vf3_pc":
            d = v.read(e)
            out[nm] = d
    v.close()
    return out

vfs = vf3info(os.path.join(G, "common.vpp_pc"),
              {"fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_bodyital_n", "fnt_head_n"})
for nm, d in sorted(vfs.items()):
    print("  %s (%d 字节):" % (nm, len(d)))
    print("     原始 hex: %s" % d[:0x30].hex(" "))
    if len(d) >= 0x30:
        ver, = struct.unpack_from("<I", d, 0x04)
        N, = struct.unpack_from("<i", d, 0x08)
        firstascii, = struct.unpack_from("<i", d, 0x0C)
        W, = struct.unpack_from("<i", d, 0x10)
        H, = struct.unpack_from("<h", d, 0x14)
        RH, = struct.unpack_from("<h", d, 0x16)
        BO, = struct.unpack_from("<i", d, 0x18)
        CS, = struct.unpack_from("<h", d, 0x1C)
        nkern, = struct.unpack_from("<i", d, 0x20)
        VO, = struct.unpack_from("<i", d, 0x24)
        print("     ver=%d N=%d firstascii=%d W=%d H=%d RenderH=%d BaseOff=%d CharSpacing=%d KernPairs=%d VertOff=%d"
              % (ver, N, firstascii, W, H, RH, BO, CS, nkern, VO))
        # 记录区起点
        base = 0x30 + nkern * 12
        print("     记录区起点 = 0x%X (0x30 + %d*12)" % (base, nkern))
        print("     记录数 N = %d, 记录区结束 = 0x%X" % (N, base + N * 16))
        print("     U 数组起点 = 0x%X, U 字节数 = %d, 剩余 = %d" %
              (base + N * 16, N * 4, len(d) - (base + N * 16) - N * 4))
        print("     尾部 hex: %s" % d[-32:].hex(" "))
    print()
