import sys, struct
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
print("文件大小", len(vf3))
print("头部 0x00-0xD0:")
for off in range(0, 0xD0, 16):
    row = vf3[off:off+16]
    print("  %04X  %s   |%s|" % (off, " ".join("%02X"%b for b in row),
        "".join(chr(b) if 32<=b<127 else "." for b in row)))
print()
print("尾部 64 字节:")
for off in range(len(vf3)-64, len(vf3), 16):
    row = vf3[off:off+16]
    print("  %04X  %s   |%s|" % (off, " ".join("%02X"%b for b in row),
        "".join(chr(b) if 32<=b<127 else "." for b in row)))
