# -*- coding: utf-8 -*-
"""从 sym stream(525) 提取符号：名字为记录尾部的 inline NUL 串（带 u32 长度前缀）。
策略：对每条记录，在 payload 里找形如 [?A-Za-z_@] 开头的可打印串（长度 >= 3），取最后一个。
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]


def stream(i):
    return b"".join(d[b * BS:(b + 1) * BS] for b in blocks[i])[:sizes[i]]


sym = stream(525)
n = len(sym)
TYPE = {0x1101: "COMPILE3", 0x1105: "OBJNAME", 0x1107: "OBJNAME_ST", 0x1108: "GPROC32",
        0x110A: "LPROC32", 0x110C: "REGREL32", 0x110D: "LDATA32", 0x110E: "PUB32",
        0x1110: "THUNK32", 0x1111: "BLOCK32", 0x1116: "LPROC32_ID", 0x1125: "UDT32_ST"}


def scan_ascii(payload):
    """返回 payload 中所有 (offset, str) 的可打印串"""
    out = []
    i = 0
    while i < len(payload):
        c = payload[i]
        if 32 <= c < 127 and (chr(c).isalnum() or chr(c) in "_@?$<>&:."):
            j = i
            while j < len(payload) and 32 <= payload[j] < 127:
                j += 1
            s = payload[i:j].decode("ascii", "replace")
            if len(s) >= 3:
                out.append((i, s))
            i = j
        else:
            i += 1
    return out


rows = []
off = 0
while off + 4 <= n:
    rlen = struct.unpack("<H", sym[off:off + 2])[0]
    if rlen < 2 or off + rlen > n:
        break
    rtype = struct.unpack("<H", sym[off + 2:off + 4])[0]
    payload = sym[off + 4:off + rlen]
    tn = TYPE.get(rtype)
    if tn:
        cands = scan_ascii(payload)
        if cands:
            rows.append((tn, off, cands[-1][0], cands[-1][1]))
    off += rlen
    if rlen % 4:
        off += 4 - (rlen % 4)

print("total typed records:", len(rows))
with open(r"F:\sr2-cn\_pdb_syms3.txt", "w", encoding="utf-8") as f:
    for tn, off, noff, nm in rows:
        f.write("%-11s off=0x%-8X name@%d %s\n" % (tn, off, noff, nm))
for kw in ["MStrings", "harList", "loadchar", "Font", "font", "Glyph", "glyph", "Vint", "vint", "ocaliz", "Localiz"]:
    hits = [(tn, off, nm) for tn, off, noff, nm in rows if kw in nm]
    print("\n[%s] %d hits" % (kw, len(hits)))
    for tn, off, nm in hits[:20]:
        print("   %-11s 0x%-8X %s" % (tn, off, nm))
