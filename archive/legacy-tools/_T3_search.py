# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOTS = [r"G:/SteamLibrary/steamapps/common/Saints Row 2"]
PAT = bytes.fromhex('f284ed87')
hits = []
skip_dirs = {'reshade-shaders', 'videos', 'DirectX', 'Microsoft.VC80.CRT', 'host64'}
n = 0
for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip_dirs]
        for f in fn:
            if f.lower().endswith(('.bak', '.log', '.dmp', '.pdb')):
                continue
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) > 60*1024*1024:
                    continue
                d = open(p, 'rb').read()
            except Exception:
                continue
            n += 1
            if PAT in d:
                hits.append((p, len(d), d.find(PAT)))
print("scanned", n)
for h in hits:
    print("HIT", h)
