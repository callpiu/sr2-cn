import os, sys, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CAND = []
for root, dirs, files in os.walk(GAME):
    for f in files:
        if f.lower().endswith((".vpp_pc", ".vpp")):
            CAND.append(os.path.join(root, f))
for root, dirs, files in os.walk(r"F:\sr2-cn\vpp_backup"):
    for f in files:
        if f.lower().endswith((".vpp_pc", ".vpp", ".orig")):
            CAND.append(os.path.join(root, f))

for p in CAND:
    try:
        v = Vpp(p); ents = v.entries()
    except Exception:
        continue
    for e in ents:
        if e["name"].startswith("fnt_chinese"):
            b = v.read(e)
            print("%-52s %-28s size=%-9d md5=%s" % (os.path.basename(p), e["name"] + "." + e["ext"], len(b), hashlib.md5(b).hexdigest()[:12]))
