import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CUR = os.path.join(G, "patch.vpp_pc")                       # 当前=汉化版
OFF = os.path.join(G, "patch.vpp_pc.official_bak")          # 官方版
for label, p in (("官方版", OFF), ("汉化版", CUR)):
    v = Vpp(p)
    print("=== %s (%d 条目, %d 字节) ===" % (label, v.num, os.path.getsize(p)))
    names = []
    for e in v.entries():
        if e["name"] in ("static_CH","static_US","voice_script_CH","platform_pc_CH","platform_PC_US","charlist_CH","fnt_chinese"):
            names.append("%-18s %-10s %8d" % (e["name"], e["ext"], e["size"]))
    for n in sorted(names): print("    " + n)
    # 列出所有 static_* / charlist_* 的名字
    st = sorted(set(e["name"] for e in v.entries() if e["name"].startswith(("static_","charlist_","platform_","voice_script_"))))
    print("    全部文本/字表条目: %s" % ", ".join(st))
    print()
print("=== 其它 VPP 里的 charlist / 字体 ===")
for f in ("common.vpp_pc","textures.vpp_pc","pegs.vpp_pc"):
    v = Vpp(os.path.join(G,f))
    hits = ["%s.%s(%d)" % (e["name"], e["ext"], e["size"]) for e in v.entries()
            if "charlist" in e["name"].lower() or "fnt_" in e["name"].lower()]
    print("  %-18s %s" % (f, ", ".join(hits[:12]) if hits else "-"))
