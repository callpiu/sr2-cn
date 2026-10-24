import os, sys
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
targets = {
  "zSHP(u16)":        "zSHP".encode("utf-16-le"),
  "ChopShop(u16)":    "ChopShop".encode("utf-16-le"),
  "chopshop(u16)":    "chopshop".encode("utf-16-le"),
  "CHOP_SHOP(u16)":   "CHOP_SHOP".encode("utf-16-le"),
  "Shop(u16)":        "Shop".encode("utf-16-le"),
  "HUD_CHOP(u16)":    "HUD_CHOP".encode("utf-16-le"),
}
print("目标字节:")
for k,v in targets.items(): print("  %-18s %s" % (k, v.hex(" ")))
print()
for root, dirs, fs in os.walk(G):
    if "_archive" in root or "reshade-shaders" in root or "_DLSS5" in root: continue
    for f in fs:
        p = os.path.join(root,f)
        try:
            if os.path.getsize(p) > 60*1024*1024: continue
            d = open(p,"rb").read()
        except Exception: continue
        for k, pat in targets.items():
            if k == "Shop(u16)": continue
            if pat in d:
                print("  %-58s %-16s @0x%X" % (os.path.relpath(p,G), k, d.find(pat)))
