# -*- coding: utf-8 -*-
import os, sys, re, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

for tag, path in (("patch", os.path.join(G,"patch.vpp_pc")),
                  ("common", os.path.join(G,"common.vpp_pc"))):
    v = Vpp(path)
    print("=== %s 中的字体资源 ===" % tag)
    for e in v.entries():
        n = (e['name'] + '.' + e['ext']).lower()
        if 'fnt' in n or 'font' in n or n.startswith('jap') or 'charlist' in n:
            print("   %-34s size=%-9d md5=%s" % (e['name']+'.'+e['ext'], e['size'],
                  hashlib.md5(v.read(e)).hexdigest()[:12]))

print("\n=== fnt_chinese.vf3_pc 头部 ===")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("fnt_chinese", "vf3_pc")
if e is None:
    for ee in v.entries():
        if ee['name']=='fnt_chinese': e = ee
print("entry:", e)
d = v.read(e)
print("size", len(d))
for off in range(0, 224, 16):
    print("  %04X  %s" % (off, ' '.join('%02x'%b for b in d[off:off+16])))
print("  ascii@0:", d[:4])
N = struct.unpack_from("<I", d, 8)[0]
print("  N@8 =", N, " -> (len-?) / N =", (len(d))/N)
