# -*- coding: utf-8 -*-
# 步骤4：检查汉化版 voice_script_CH / platform_pc_CH 按 B 解码是否正常
# 字幕不走 static_CH（已证实 100% 正常），怀疑走 voice_script_CH
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

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


cn = Vpp(CN)
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
print("B =", len(B))

def load(name, ext):
    d = cn.read(cn.find(name, ext))
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

def txt(sl):
    r = []
    for s in sl:
        i = s - 32
        r.append(B[i] if 0 <= i < len(B) else "{%d}" % s)
    return "".join(r)

for name in ("voice_script_CH", "platform_pc_CH"):
    d, count, ptrs = load(name, "le_strings")
    print("\n=== %s : count=%d ===" % (name, count))
    # 统计越界与低概率字
    oob = 0
    freq = {}
    for i in range(count):
        try:
            _, _, sl = rec(d, ptrs[i])
        except Exception:
            continue
        for s in sl:
            if s - 32 >= len(B) or s - 32 < 0:
                oob += 1
            else:
                c = B[s - 32]
                if "\u4e00" <= c <= "\u9fff":
                    freq[c] = freq.get(c, 0) + 1
    print("越界槽位 =", oob)
    print("样本文本（前 12 条含中文的）:")
    shown = 0
    for i in range(count):
        try:
            _, _, sl = rec(d, ptrs[i])
        except Exception:
            continue
        t = txt(sl)
        if re.search(r"[\u4e00-\u9fff]{4,}", t):
            print("   ", t[:70])
            shown += 1
            if shown >= 12:
                break
    # 关键：搜「兄弟」「保护」相关
    hits = 0
    for i in range(count):
        try:
            _, _, sl = rec(d, ptrs[i])
        except Exception:
            continue
        t = txt(sl)
        if "兄弟" in t or "保护" in t or "保護" in t:
            print("  [命中]", t[:70])
            hits += 1
            if hits >= 8:
                break
    if not hits:
        print("  (无 兄弟/保护 命中)")
