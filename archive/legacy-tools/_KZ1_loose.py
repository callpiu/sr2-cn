# -*- coding: utf-8 -*-
# 解码 Juiced 松散 le_strings，看活动字幕文本到底来自哪个文件
import sys, struct, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
f = Font(os.path.join(G, "patch.vpp_pc"))
CL = f.charlist
TARGETS = [bytes.fromhex(h) for h in ["84F287ED", "10AF1E62", "EC2D9F07", "95A79EDC", "343FEA1F", "E52F931A"]]
TARGETS = [bytes([t[1], t[0], t[3], t[2]]) for t in TARGETS]


def dec(slots, CL):
    return "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in slots)


def parse(path, tag):
    if not os.path.exists(path):
        print("[%s] 不存在" % tag)
        return
    d = open(path, "rb").read()
    print("\n=== %s  size=%d ===" % (tag, len(d)))
    try:
        magic, ver, buckets, count = struct.unpack_from("<I H H I", d, 0)
    except Exception as e:
        print("  解析失败", e)
        return
    print("  magic=%08X ver=%d buckets=%d count=%d" % (magic, ver, buckets, count))
    if magic != 0xA84C7F73:
        print("  不是 le_strings")
        return
    po = 12 + buckets * 8
    for idx in range(count):
        p = struct.unpack_from("<I", d, po + idx * 4)[0]
        if p + 4 > len(d):
            continue
        b4 = d[p:p + 4]
        w = p + 4
        sl = []
        while w + 2 <= len(d):
            s = struct.unpack_from(">H", d, w)[0]
            if s == 0:
                break
            sl.append(s)
            w += 2
        mark = "  ★目标" if b4 in TARGETS else ""
        txt = dec(sl, CL)
        if mark or len(txt) < 40:
            print("  [%3d] %s slots=%-3d %s%s" % (idx, b4.hex().upper(), len(sl), txt[:70], mark))


parse(os.path.join(G, "Mods/JUICED - Strings/juiced_CH.le_strings"), "松散 juiced_CH.le_strings")
parse(os.path.join(G, "Mods/JUICED - Strings/patch_ch.le_strings"), "松散 patch_ch.le_strings")
parse(os.path.join(G, "DLC/Text/dlc_ch.le_strings"), "DLC dlc_ch.le_strings")

# vpp 内 static_CH 作对照
d = f.v.read(f.v.find("static_CH", "le_strings"))
magic, ver, buckets, count = struct.unpack_from("<I H H I", d, 0)
po = 12 + buckets * 8
print("\n=== vpp 内 static_CH（只列目标记录）===")
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
    print("  [%5d] %s slots=%-3d %s" % (idx, b4.hex().upper(), len(sl), dec(sl, CL)[:70]))
