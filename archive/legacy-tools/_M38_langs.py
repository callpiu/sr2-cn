# -*- coding: utf-8 -*-
# 检验：引擎是否取了日文/韩文等其它语言版的同一 id 记录
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"

TARGETS = [(0x8848, 0x0138), (0x84F2, 0x87ED), (0x510C, 0x44FC)]


def parse_charlist(raw):
    out = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="): continue
        for tok in s.split():
            if tok.isdigit(): out.append(chr(int(tok)))
    return out


vv = Vpp(VANILLA)
cn = Vpp(CN)

# 官方表（各语言共用官方 vpp 里的 charlist）
TABLES = {}
for e in vv.entries():
    n = (e["name"] or "")
    if (e["ext"] or "").lower() == "txt" and n.lower().startswith("charlist"):
        TABLES[n] = parse_charlist(vv.read(e))
print("可用 charlist:", {k: len(v) for k, v in TABLES.items()})
TABLES["charlist_CH(汉化)"] = [chr(c) for c in Font(CN).charlist]

# 各语言 le_strings
LANGS = [("static_JP", "JP"), ("static_SK", "SK"), ("static_CZ", "CZ"),
         ("static_US", "US"), ("static_DE", "DE")]
for lang, tag in LANGS:
    e = vv.find(lang, "le_strings")
    if not e:
        print("%s 未找到" % lang); continue
    d = vv.read(e)
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    print("\n=== %s (count=%d) ===" % (lang, count))
    for id1, id2 in TARGETS:
        for i in range(count):
            p = ptrs[i]
            if p + 6 > len(d):
                continue
            a, b_ = struct.unpack_from("<HH", d, p)
            if (a, b_) != (id1, id2):
                continue
            q = p + 4
            # 英文表是 UTF-16BE；其它语言未知，先 dump 原始
            chunk = d[q:q + 60]
            print("  [%04X.%04X] 原始: %s" % (id1, id2, chunk.hex(" ")[:80]))
            # 试 UTF-16BE 解码
            try:
                s = chunk.decode("utf-16-be", "ignore").split("\x00")[0]
                if s:
                    print("      UTF-16BE: %s" % s[:60])
            except Exception:
                pass
            break
