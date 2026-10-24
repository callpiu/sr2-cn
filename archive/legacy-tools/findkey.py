import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEYS = [b"SUI_OPTIONS_TITLE", b"SUI_LOADING", b"SUI_OPTIONS_WEAPON_SWITCH_SOUND"]
for vf in ("patch.vpp_pc","common.vpp_pc","pegs.vpp_pc"):
    p = os.path.join(G, vf)
    if not os.path.exists(p): continue
    try: v = Vpp(p)
    except Exception as ex: print("  %s 打开失败 %s" % (vf, ex)); continue
    print("=== %s (%d 条目) ===" % (vf, v.num))
    for e in v.entries():
        try: d = v.read(e)
        except Exception: continue
        for k in KEYS:
            if k in d:
                print("  %-30s %-12s %9d  含 %s" % (e["name"], e["ext"] or "-", e["size"], k.decode()))
    # 顺便找名字像 strings 的
print()
print("=== common.vpp_pc 里的 le_strings / 文本资源 ===")
p = os.path.join(G,"common.vpp_pc")
if os.path.exists(p):
    v = Vpp(p)
    for e in v.entries():
        if e["ext"] in ("le_strings","txt","xtbl") or "string" in e["name"].lower() or "menus" in e["name"].lower():
            print("  %-36s %-12s %9d" % (e["name"], e["ext"] or "-", e["size"]))
