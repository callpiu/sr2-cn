import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 全盘搜索 static_CH / voice_script_CH / platform_pc_CH ===")
hits = []
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup","reshade-shaders","_vanilla_test")): continue
    for f in fs:
        p = os.path.join(root,f)
        # 松散文件
        if f.lower() in ("static_ch.le_strings","voice_script_ch.le_strings","platform_pc_ch.le_strings"):
            hits.append(("LOOSE", os.path.relpath(p,G), os.path.getsize(p)))
        # VPP
        if f.lower().endswith(".vpp_pc"):
            try: v = Vpp(p)
            except Exception: continue
            for e in v.entries():
                if e["name"] in ("static_CH","voice_script_CH","platform_pc_CH"):
                    hits.append((f, "%s.%s" % (e["name"], e["ext"]), e["size"]))
for src, name, sz in hits:
    print("  %-24s %-40s %d" % (src, name, sz))
print()
print("=== common.vpp_pc 里所有 le_strings ===")
v = Vpp(os.path.join(G,"common.vpp_pc"))
ls = [e for e in v.entries() if e["ext"]=="le_strings"]
print("  共 %d 个" % len(ls))
for e in sorted(ls, key=lambda x: x["name"])[:30]:
    print("    %-28s %8d" % (e["name"], e["size"]))
