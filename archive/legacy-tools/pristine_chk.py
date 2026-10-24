import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
# 1) 原厂繁体 patch.vpp_pc 里搜
P = r"F:\sr2-cn\pristine\patch.vpp_pc"
v = Vpp(P)
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
def slot_seq(s):
    out=b""
    for ch in s:
        if ord(ch) in CPS: out += (CPS.index(ord(ch))+0x20).to_bytes(2,"little")
    return out
pats = {"音效音量": slot_seq("音效音量"), "武器切换音效": slot_seq("武器切换音效"),
        "加载": slot_seq("加载"), "载入": slot_seq("载入")}
for k,p in pats.items():
    print("  原厂繁体 搜 %-12s (%s): %s" % (k, p[:16].hex(), "有" if p and p in v.data else "无"))
print()
# 2) 第三方补丁的 static_CH 里搜这两个 key 的英文形式
d = bytes(v.read(v.find("static_CH","le_strings"))) if v.find("static_CH") else None
print("原厂 static_CH: %s" % ("有" if d else "无"))
# 3) 列出原厂 patch 里所有 le_strings 资源
print()
print("=== 原厂 patch.vpp_pc 的文本资源 ===")
for e in v.entries():
    if e["ext"] == "le_strings":
        print("  %-30s %9d" % (e["name"], e["size"]))
