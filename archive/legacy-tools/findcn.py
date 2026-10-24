import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
# 目标：找到含「音效音量」或「SUI_OPTIONS_TITLE」的字符串表
TARGET_CN = "音效音量"
TARGET_KEY = "SUI_OPTIONS_TITLE"
# 槽位序列：值 = 索引+0x20
def slot_seq(s):
    out = b""
    for ch in s:
        if ord(ch) in CPS:
            out += (CPS.index(ord(ch))+0x20).to_bytes(2,"little")
    return out
pats = {"音效音量(槽位)": slot_seq(TARGET_CN),
        "SUI_OPTIONS_TITLE(ascii)": TARGET_KEY.encode("ascii")}
print("搜索目标: %s" % {k: v[:20].hex() for k,v in pats.items()})
print()
hits = []
for e in v.entries():
    name, ext, size = e["name"], e["ext"], e["size"]
    if ext in ("lua","g_peg_pc","vf3_pc","peg","chunk","cts","xtbl"): continue
    if size > 3_000_000: continue
    try: d = bytes(v.read(e))
    except Exception: continue
    for label, pat in pats.items():
        if pat and pat in d:
            hits.append((name, ext, size, label))
for h in hits: print("  命中 %-30s %-12s %9d  %s" % h)
if not hits: print("  未命中")
