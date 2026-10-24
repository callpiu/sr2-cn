# -*- coding: utf-8 -*-
# 决定性：哪些字符串走 hud_msg（thin_overlay）路径？
# 搜所有 lua 里调用 hud_message / HUD_REGION_SUBTITLES / help 的地方
import sys, os, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
cn = Vpp(os.path.join(G, "patch.vpp_pc"))

PAT = re.compile(r"hud_message|hud_msg|HUD_REGION|subtitle", re.I)

print("=== 调用 hud_message / HUD_REGION 的 lua ===")
for e in cn.entries():
    if (e["ext"] or "").lower() != "lua":
        continue
    try:
        d = cn.read(e)
    except Exception:
        continue
    if not PAT.search(d.decode("latin-1")):
        continue
    n = d.decode("utf-8", "replace")
    lines = [(i + 1, l.strip()) for i, l in enumerate(n.split("\n")) if PAT.search(l)]
    if lines:
        print("\n--- %s.lua (%d B) ---" % (e["name"], len(d)))
        for ln, l in lines[:12]:
            print("  %4d| %s" % (ln, l[:100]))
