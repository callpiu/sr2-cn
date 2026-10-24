# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
files = [r"patch.vpp_pc"] + [f for f in os.listdir(G)
        if f.startswith('patch.vpp_pc.') and ('bak' in f) and os.path.getsize(os.path.join(G, f)) > 40_000_000]
PAT = bytes.fromhex('f284ed87')
for fn in files:
    p = os.path.join(G, fn)
    d = open(p, 'rb').read()
    i = d.find(PAT)
    if i < 0:
        print(fn, "no hit"); continue
    sl = []
    o = i + 4
    for _ in range(60):
        v = struct.unpack_from('>H', d, o)[0]; o += 2
        if v == 0: break
        sl.append(v)
    print("%-58s F284ED87 -> %s" % (fn, sl))
