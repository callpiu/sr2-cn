import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p, name, ext):
    v = Vpp(p); return v.read(v.find(name, ext))
pairs = [
  ("mine (patch)",   get(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc")),
  ("mine (textures)",get(os.path.join(G,"textures.vpp_pc"),"fnt_chinese",None)),
  ("official (patch.orig)", get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig","fnt_chinese","g_peg_pc")),
  ("official (tex.orig)",   get(r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig","fnt_chinese",None)),
]
for tag, b in pairs:
    print("=== %s  (%d bytes) ===" % (tag, len(b)))
    for off in range(0, 64, 4):
        v = struct.unpack_from("<I", b, off)[0]
        print("   +%02X = %-12d (0x%X)" % (off, v, v))
    print()
