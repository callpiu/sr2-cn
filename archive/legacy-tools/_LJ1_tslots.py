# -*- coding: utf-8 -*-
# 步骤2：官方繁体表 T vs 汉化简体表 B；并用 T 解码 static_CH 文本
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN      = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//"):
            continue
        if s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


vv = Vpp(VANILLA)
cn = Vpp(CN)

t_raw = vv.read(vv.find("charlist_CH", "txt"))
b_raw = cn.read(cn.find("charlist_CH", "txt"))
T, B = parse_charlist(t_raw), parse_charlist(b_raw)
print("官方繁体表 T = %d 项，简体表 B = %d 项" % (len(T), len(B)))
print("T 按码点递增:", all(ord(T[i]) < ord(T[i + 1]) for i in range(len(T) - 1)))
print("B 按码点递增:", all(ord(B[i]) < ord(B[i + 1]) for i in range(len(B) - 1)))

TS, BS = set(T), set(B)
print("\n只在 T 中（繁体/扩展）的字数 =", len(TS - BS))
print("只在 B 中的字数 =", len(BS - TS))

# 字幕A 的乱码字检验
print("\n=== 关键字的表内位置 ===")
for ch in "你兄弟需要保們護位该":
    print("  %s  T序=%s  B序=%s" % (ch,
          T.index(ch) if ch in TS else "--",
          B.index(ch) if ch in BS else "--"))

# 用 T 解码 static_CH：槽位 s -> T[s]
# le_strings 格式（此前确证）：
#   magic 0xA84C7F73 / ver u16 / buckets u16 / count u32 / bucket表 / pointer数组 / 记录
#   记录 = [id1 LE u16][id2 LE u16] + 大端 u16 槽位流 + 0x0000
data = vv.read(vv.find("static_CH", "le_strings"))
print("\nstatic_CH 大小 =", len(data), " magic = %08X" % struct.unpack_from("<I", data, 0)[0])
ver, buckets = struct.unpack_from("<HH", data, 4)
count, = struct.unpack_from("<I", data, 8)
print("ver=%d buckets=%d count=%d" % (ver, buckets, count))

off = 12 + buckets * 8
ptrs = struct.unpack_from("<%dI" % count, data, off)
off += count * 4

def decode_rec(start, table):
    """从 start 起解一条记录：id1/id2 + 槽位流(大端u16, 0 结尾)"""
    id1, id2 = struct.unpack_from("<HH", data, start)
    p = start + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", data, p)
        p += 2
        if s == 0:
            break
        if s < 32 or s - 32 >= len(table):
            out.append("{%d}" % s); continue
        out.append(table[s - 32])
    return id1, id2, "".join(out), p


# 抽 20 条样本看内容
print("\n=== 用官方繁体表 T 解码的前 20 条 ===")
shown = 0
for i in range(min(count, 400)):
    try:
        id1, id2, txt, _ = decode_rec(ptrs[i], T)
    except Exception as ex:
        continue
    if len(txt) >= 6 and re.search(r"[\u4e00-\u9fff]", txt):
        print("  [%04X.%04X] %s" % (id1, id2, txt[:60]))
        shown += 1
        if shown >= 20:
            break

# 统计：所有记录里有多少字符不在 B 中（按 T 解码）
missing = {}
tot = 0
for i in range(count):
    try:
        _, _, txt, _ = decode_rec(ptrs[i], T)
    except Exception:
        continue
    for ch in txt:
        if "\u4e00" <= ch <= "\u9fff":
            tot += 1
            if ch not in BS:
                missing[ch] = missing.get(ch, 0) + 1
print("\nstatic_CH 总汉字数 = %d" % tot)
print("其中不在简体表 B 中的不同字符数 = %d，出现次数 = %d" % (len(missing), sum(missing.values())))
top = sorted(missing.items(), key=lambda x: -x[1])[:40]
print("Top40 缺字:", " ".join("%s(%d)" % (c, n) for c, n in top))
