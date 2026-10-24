# -*- coding: utf-8 -*-
"""GL1: 回退 exe + 定位 static_CH 里那两条记录的结构（为降级做准备）。"""
import sys, os, shutil, struct, re, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGETS = (0xF284ED87, 0xAF10621E)

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---- 1) exe 回退到原版 ----
exe = os.path.join(G, "SR2_pc.exe")
print("exe 改前 md5:", md5f(exe))
shutil.copy2(r"F:\sr2-cn\SR2_pc.exe.orig", exe)
print("exe 回退后 md5:", md5f(exe), "(应 = 717786be27a34dda5a86bf82930b2ced)")

# ---- 2) 松散 static_CH ----
print("\n=== 松散 le_strings ===")
for d in (os.path.join(G, "Mods"), G):
    if not os.path.isdir(d):
        continue
    for fn in os.listdir(d):
        if fn.lower().endswith(".le_strings"):
            p = os.path.join(d, fn)
            b = open(p, "rb").read()
            mg = struct.unpack_from("<I", b, 0)[0] if len(b) >= 4 else 0
            print("  %-50s %8d B  magic=0x%08X" % (os.path.relpath(p, G), len(b), mg))

# ---- 3) patch.vpp_pc 里的 static_CH ----
print("\n=== patch.vpp_pc/static_CH ===")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
for e in v.entries():
    if (e["name"] or "") == "static_CH":
        raw = v.read(e)
        print("  static_CH.%s  %d B  md5=%s" % (e["ext"], len(raw), md5f.__name__ and hashlib.md5(raw).hexdigest()[:12]))
        print("  head:", " ".join("%02X" % c for c in raw[:32]))
        for t in TARGETS:
            for bo in ("<I", ">I"):
                pat = struct.pack(bo, t)
                pos = [m.start() for m in re.finditer(re.escape(pat), raw)]
                if pos:
                    print("  id 0x%08X (%s) @ %s" % (t, bo, pos))
