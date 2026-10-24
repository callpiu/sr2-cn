# -*- coding: utf-8 -*-
import sys, os, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
skip = {'reshade-shaders', 'videos', 'DirectX', 'Microsoft.VC80.CRT', 'host64'}
out = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in skip]
    for f in fn:
        p = os.path.join(dp, f)
        low = f.lower()
        try:
            sz = os.path.getsize(p)
        except Exception:
            continue
        if sz > 200_000_000 or sz < 10:
            continue
        if 'charlist' in low or low.endswith('.txt'):
            try:
                d = open(p, 'rb').read(400000)
            except Exception:
                continue
            if b'ENDOFFILE' in d or b'count=' in d[:200] or 'charlist' in low:
                out.append((p, sz))
for p, sz in out:
    print(sz, p)
