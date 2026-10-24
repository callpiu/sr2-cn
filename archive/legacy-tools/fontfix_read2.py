# -*- coding: utf-8 -*-
"""读 pegs 描述符 + vf3 头部，搞清 fnt_body_n/s 与 fnt_chinese 的结构差异。"""
import os, struct, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp, parse_vf3_header

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- pegs 描述符 ----
print("=== pegs.vpp_pc 字体描述符（完整 hex）===")
with LightVpp(os.path.join(G, "pegs.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_head_n", "fnt_bodyital_n"):
            d = pv.read(e)
            print("  %s (%d 字节, body=0x%X):" % (nm, len(d), e["body"]))
            for k in range(0, len(d), 16):
                seg = d[k:k + 16]
                print("     +%02X  %s  |%s|" % (k,
                      " ".join("%02X" % x for x in seg),
                      "".join(chr(x) if 32 <= x < 127 else "." for x in seg)))
            print()

# ---- textures 图集：读每个图集的前 0x40 字节（含尺寸信息）----
print("=== textures.vpp_pc 字体图集头部（前 0x40 字节）===")
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        nm = tv.name(e)
        if nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_head_n"):
            d = tv.read(e)
            print("  %s (%d 字节, body=0x%X):" % (nm, len(d), e["body"]))
            print("     %s" % d[:0x40].hex(" "))
            # 尝试按 DDS 解
            if d[:4] == b"DDS ":
                h, w, sz, fl, = struct.unpack_from("<IIII", d, 12)
                print("     DDS: H=%d W=%d linearSize=%d flags=0x%X" % (h, w, sz, fl))
            else:
                print("     非 DDS 头，tag=%r" % d[:4])
            print()

# ---- common vf3 头部 ----
print("=== common.vpp_pc vf3 头部字段 ===")
with LightVpp(os.path.join(G, "common.vpp_pc")) as cv:
    for e in cv.entries():
        nm = cv.name(e)
        ex = cv.ext(e)
        if ex == "vf3_pc" and nm.startswith("fnt_"):
            d = cv.read(e)
            h = parse_vf3_header(d)
            print("  %-18s %6d 字节" % (nm, len(d)))
            print("     ver=%(ver)d N=%(N)d firstascii=%(firstascii)d W=%(W)d H=%(H)d "
                  "RenderH=%(RenderH)d CharSpacing=%(CharSpacing)d KernPairs=%(KernPairs)d VertOff=%(VertOff)d" % h)
            base = 0x30 + h["KernPairs"] * 12
            print("     记录区 0x%X..0x%X, U 起点 0x%X, 尾部 32B: %s" %
                  (base, base + h["N"] * 16, base + h["N"] * 16, d[-32:].hex(" ")))
            print()
