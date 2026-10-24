# -*- coding: utf-8 -*-
# 步骤5（决定性）：字幕文本本身就有错字，不是渲染 bug？
# 在官方繁体表 + 汉化简体表下，搜直升机突击相关句子
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


vv, cn = Vpp(VANILLA), Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))

def load(v, name, ext="le_strings"):
    d = v.read(v.find(name, ext))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs

def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        out.append(s)
    return id1, id2, out

def txt(sl, table):
    r = []
    for s in sl:
        i = s - 32
        r.append(table[i] if 0 <= i < len(table) else "{%d}" % s)
    return "".join(r)

KEYS = ["直升", "直升機", "直升机", "兄弟", "保護", "保护", "突襲", "突袭"]
for tag, v, tab in (("官方繁体", vv, T), ("汉化简体", cn, B)):
    for name in ("static_CH", "voice_script_CH", "platform_pc_CH"):
        try:
            d, count, ptrs = load(v, name)
        except Exception as e:
            print("%s/%s: %s" % (tag, name, e)); continue
        print("\n########## %s / %s (count=%d) ##########" % (tag, name, count))
        for i in range(count):
            try:
                a, b_, sl = rec(d, ptrs[i])
            except Exception:
                continue
            t = txt(sl, tab)
            if len(t) < 4:
                continue
            hit = [k for k in KEYS if k in t]
            if hit:
                print("  [%04X.%04X] <%s> %s" % (a, b_, ",".join(hit), t[:78]))
