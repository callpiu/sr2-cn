import os
d = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main"
p = None
for root, dirs, fs in os.walk(d):
    if "Memory.cpp" in fs: p = os.path.join(root,"Memory.cpp"); break
s = open(p, encoding="utf-8", errors="replace").read()
lines = s.split("\n")
print("=== Memory.cpp 95..135 行 ===")
for i in range(94, min(135, len(lines))):
    print("  %4d: %s" % (i+1, lines[i].rstrip()))
