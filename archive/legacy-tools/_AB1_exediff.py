# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
a = open(os.path.join(G, 'SR2_pc.exe'), 'rb').read()
b = open(os.path.join(G, 'SR2_pc.exe.bak'), 'rb').read()
c = open(os.path.join(G, 'sr2_pc_unpatched.exe'), 'rb').read()
print("SR2_pc.exe       ", len(a))
print("SR2_pc.exe.bak   ", len(b))
print("unpatched        ", len(c))

def diffs(x, y, name):
    n = min(len(x), len(y))
    runs = []
    i = 0
    while i < n:
        if x[i] != y[i]:
            j = i
            while j < n and x[j] != y[j]:
                j += 1
            runs.append((i, j - i))
            i = j
        else:
            i += 1
    print("%s : %d diff runs, total %d bytes" % (name, len(runs), sum(r[1] for r in runs)))
    for off, ln in runs[:40]:
        print("   0x%08X len=%d" % (off, ln))
    return runs

diffs(a, b, "exe vs exe.bak")
print()
diffs(a, c[:len(a)], "exe vs unpatched(prefix)")
