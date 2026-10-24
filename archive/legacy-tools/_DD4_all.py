import sys, os, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
for f in ("common.vpp_pc","patch.vpp_pc","textures.vpp_pc"):
    p = os.path.join(G,f)
    v = Vpp(p)
    print("=== %s (%d bytes) ===" % (f, os.path.getsize(p)))
    for e in v.entries():
        n = e['name']
        if 'fnt_chinese' in n or 'charlist' in n:
            b = v.read(e)
            print("   %-24s ext=%-10s size=%8d md5=%s" % (n, e.get('ext'), len(b), hashlib.md5(b).hexdigest()[:12]))
