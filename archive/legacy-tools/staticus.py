import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
# static_US：用英文 charlist? 先看它的原始字节里有没有 ASCII 的 SUI_ key
e = v.find("static_US") or v.find("static_us")
print("static_US 条目: %s" % (e and e["name"]))
if not e:
    for x in v.entries():
        if x["name"].lower().startswith("static_us"): e = x; break
if e:
    d = bytes(v.read(e))
    print("  %d 字节" % len(d))
    for k in (b"SUI_OPTIONS_TITLE", b"SUI_LOADING_9", b"SUI_OPTIONS_WEAPON_SWITCH_SOUND"):
        print("  含 %-34s %s" % (k.decode(), k in d))
    # 找 ASCII 文本片段
    runs = re.findall(rb'[ -~]{8,60}', d)
    hits = [r.decode() for r in runs if any(w in r for w in (b"SOUND", b"Audio", b"VOLUME", b"Loading", b"OPTIONS"))]
    print("  含关键词的 ASCII 片段 (前 20):")
    for h in hits[:20]: print("     %s" % h)
