import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
for nm in ("HUD_text","MissionText","Activity_text","Gang_Names","Hoods","Menus_text","Item_text"):
    e = v.find(nm)
    if not e: print("  %-14s 未找到" % nm); continue
    d = bytes(v.read(e))
    magic = d[:4]
    print("  %-14s %8d 字节  magic=%r  前16: %s" % (nm, len(d), magic, d[:16].hex(" ")))
print()
# 在 Gang_Names / Hoods 里找中文（UTF-8 或 UTF-16）
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
for nm in ("Gang_Names","Hoods"):
    e = v.find(nm)
    d = bytes(v.read(e))
    print("=== %s (%d 字节) ===" % (nm, len(d)))
    for enc in ("utf-8","utf-16-le"):
        try:
            s = d.decode(enc)
        except Exception: continue
        has = [c for c in s if 0x4E00 <= ord(c) <= 0x9FFF]
        print("  按 %s 解码: 总长 %d, 含汉字 %d 个 %s" % (enc, len(s), len(has), "".join(has[:30])))
    # 搜槽位序列
    for w in ("三王","丈王"):
        if all(ord(c) in CPS for c in w):
            pat = b"".join(struct.pack("<H", CPS.index(ord(c))+0x20) for c in w)
            print("  槽位序列 %r: %s" % (w, "命中" if pat in d else "未命中"))
    print()
