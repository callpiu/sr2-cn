import os, re
d = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main"
for f in ("Memory.cpp",):
    p = None
    for root, dirs, fs in os.walk(d):
        if f in fs:
            p = os.path.join(root,f); break
    if not p: print("%s 未找到" % f); continue
    s = open(p, encoding="utf-8", errors="replace").read()
    lines = s.split("\n")
    print("=== %s (%d 行) ===" % (f, len(lines)))
    for i, ln in enumerate(lines, 1):
        if re.search(r'GetValue|patchInt|patchNop|patchByte|permanent|Pool|pool', ln):
            print("  %4d: %s" % (i, ln.rstrip()[:150]))
