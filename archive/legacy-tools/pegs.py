import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
# 找 pegs.vpp_pc
cands = [os.path.join(W,"pristine"), r"G:\SteamLibrary\steamapps\common\Saints Row 2"]
for base in cands:
    p = os.path.join(base, "pegs.vpp_pc")
    if os.path.exists(p):
        print("找到 %s (%d 字节)" % (p, os.path.getsize(p)))
        v = Vpp(p)
        for e in v.entries():
            if "chinese" in e["name"].lower():
                print("  条目 %s.%s  size=%d off=%d" % (e["name"], e["ext"], e["size"], e["body"]))
                d = bytes(v.read(e))
                print("  前 64 字节: %s" % d[:64].hex(' '))
                print("  u16 @0x1C = %d (宽?)" % struct.unpack_from("<H", d, 0x1C)[0])
                print("  u16 @0x1E = %d (高?)" % struct.unpack_from("<H", d, 0x1E)[0])
                print("  u16 @0x20 = %d (格式?)" % struct.unpack_from("<H", d, 0x20)[0])
                print("  u32 @0x34 = %d (大小?)" % struct.unpack_from("<I", d, 0x34)[0])
        break
