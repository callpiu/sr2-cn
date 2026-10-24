# -*- coding: utf-8 -*-
# 决定性测试：记录里的槽位值 vs 汉化字符表索引
# 若槽位 = 官方表索引+0x20（而非汉化表），则引擎查表必然错位 —— 这就是根因
import sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
B = f.charlist
fv = Font(r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017")
OFF = fv.charlist

d = f.v.read(f.v.find("static_CH", "le_strings"))
magic, ver, buckets, count = struct.unpack_from("<I H H I", d, 0)
po = 12 + buckets * 8


def dec(slots, CL):
    return "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in slots)


TARGETS = [bytes.fromhex(h) for h in ["84F287ED", "10AF1E62", "EC2D9F07",
                                      "95A79EDC", "343FEA1F", "E52F931A"]]
TARGETS = [bytes([t[1], t[0], t[3], t[2]]) for t in TARGETS]

print("汉化表 B = %d 项，官方表 OFF = %d 项\n" % (len(B), len(OFF)))

for idx in range(count):
    p = struct.unpack_from("<I", d, po + idx * 4)[0]
    b4 = d[p:p + 4]
    if b4 not in TARGETS:
        continue
    w = p + 4
    sl = []
    while w + 2 <= len(d):
        s = struct.unpack_from(">H", d, w)[0]
        if s == 0:
            break
        sl.append(s)
        w += 2
    tag = b4.hex().upper()
    print("=== %s  idx=%d  slots=%d ===" % (tag, idx, len(sl)))
    print("  用汉化表B解码 :", dec(sl, B))
    print("  用官方表OFF解码:", dec(sl, OFF))
    print()
    print("  逐槽位核对（只列可见汉字）:")
    print("    %-4s %-8s %-8s %-10s %-10s %s" % ("字", "实际槽位", "B索引+32", "OFF索引+32", "OFF索引", "判定"))
    txt = dec(sl, B)
    for k, (w_, c) in enumerate(zip(sl, txt)):
        if not ("\u4e00" <= c <= "\u9fff"):
            continue
        bIdx = B.index(ord(c)) if ord(c) in B else None
        oIdx = OFF.index(ord(c)) if ord(c) in OFF else None
        ok = "槽位=B索引+32 ✓" if (bIdx is not None and w_ == bIdx + 32) else \
             ("槽位=OFF索引+32 ✓" if (oIdx is not None and w_ == oIdx + 32) else "都不符 ✗")
        print("    %-4s %-8d %-8s %-10s %-10s %s" % (
            c, w_, bIdx + 32 if bIdx is not None else "-",
            oIdx + 32 if oIdx is not None else "-", oIdx if oIdx is not None else "-", ok))
    print()
