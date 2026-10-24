import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
print("=== JUICED - Strings 目录里所有 .cxt / .le_strings ===")
for f in sorted(os.listdir(J)):
    p = os.path.join(J,f)
    if not os.path.isfile(p): continue
    if f.endswith((".cxt",)):
        s = open(p, encoding="utf-8", errors="replace").read()
        ks = re.findall(r'\[([A-Za-z0-9_,]+)\]', s)
        sui = [k for k in ks if k.upper().startswith("SUI")]
        print("  %-28s %6d 字节  %3d keys  SUI_ %d 个" % (f, len(s.encode()), len(ks), len(sui)))
        if sui: print("      %s" % " ".join(sui[:14]))
