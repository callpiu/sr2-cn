# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2\Mods"
PAT = bytes.fromhex('f284ed87')

def slots(d, i, n=60):
    o = i + 4
    out = []
    for _ in range(n):
        v = struct.unpack_from('>H', d, o)[0]; o += 2
        if v == 0:
            break
        out.append(v)
    return out

for fn in sorted(os.listdir(G)):
    if not fn.startswith('static_') or not fn.endswith('.le_strings'):
        continue
    d = open(os.path.join(G, fn), 'rb').read()
    i = d.find(PAT)
    if i < 0:
        print(fn, "no F284ED87")
        continue
    print("%-28s %s" % (fn, slots(d, i)))
