# -*- coding: utf-8 -*-
# 关键检验：繁体字 們/護 是否在简体 charlist B 里？
import sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
raw = f.v.read(f.cl_entry).decode("utf-8")
B = []
for L in raw.split("\r\n"):
    s = L.strip()
    if s.startswith("//") or not s or s.startswith("count="):
        continue
    for tok in s.split():
        if tok.isdigit():
            B.append(chr(int(tok)))
S = set(B)
print("B 长度 =", len(B), " 唯一 =", len(S))
print("B 是否严格按码点递增:", all(ord(B[i]) < ord(B[i+1]) for i in range(len(B)-1)))

tests = {
    "們(繁)": 0x5011, "们(简)": 0x4EEC,
    "護(繁)": 0x8B77, "护(简)": 0x62A4,
    "進(繁)": 0x9032, "进(简)": 0x8FDB,
    "擊(繁)": 0x6483, "击(简)": 0x51FB,
    "開(繁)": 0x958B, "开(简)": 0x5F00,
    "車(繁)": 0x8ECA, "车(简)": 0x8F66,
    "東(繁)": 0x6771, "东(简)": 0x4E1C,
    "麼(繁)": 0x9EBC, "么(简)": 0x4E48,
    "來(繁)": 0x4F86, "来(简)": 0x6765,
}
print("\n%-10s %-8s %-8s" % ("字", "码点", "在B中"))
for name, cp in sorted(tests.items(), key=lambda x: x[1]):
    print("%-10s U+%04X   %s" % (name, cp, "YES" if chr(cp) in S else "NO"))

# 统计：B 里有多少个汉字落在「常见繁体专属区」
trad_only = [c for c in B if 0x4E00 <= ord(c) <= 0x9FFF]
print("\nB 中 CJK 基本区字符数 =", len(trad_only))

# 检查 le_strings 里实际文本用的是什么字 —— 先定位字幕记录
print("\n=== 从 patch.vpp_pc 取 static_CH 文本 ===")
from sr2font import Vpp
v = Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
names = [n for n in v.names() if "static" in n.lower()]
print("含 static 的条目:", names)
