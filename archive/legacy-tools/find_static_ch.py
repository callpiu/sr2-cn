import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 各 VPP 里是否含 static_CH / voice_script_CH / platform_pc_CH ===")
for f in sorted(os.listdir(G)):
    if not f.lower().endswith(".vpp_pc"): continue
    p = os.path.join(G, f)
    try: v = Vpp(p)
    except Exception as ex:
        print("  %-24s 打开失败: %s" % (f, ex)); continue
    hits = []
    for e in v.entries():
        if e["name"] in ("static_CH","voice_script_CH","platform_pc_CH","static_US","charlist_CH","fnt_chinese"):
            hits.append("%s.%s(%d)" % (e["name"], e["ext"], e["size"]))
    print("  %-24s %6d 条目  %s" % (f, v.num, ", ".join(hits) if hits else "-"))
