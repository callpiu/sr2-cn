import struct, numpy as np
def hdr(b, tag):
    print("---", tag, "len", len(b))
    print("  magic", b[0:4], " N@8", struct.unpack_from("<I",b,8)[0],
          " w@C", struct.unpack_from("<I",b,0xC)[0],
          " h@10", struct.unpack_from("<I",b,0x10)[0])
    for off in (0x14,0x18,0x1C,0x20,0x24,0x28,0x2C,0x30,0x34,0x38,0x3C,0x40):
        v = struct.unpack_from("<I",b,off)[0]
        if v: print("   @%02X = %d (0x%X)" % (off, v, v))
    s = b[0x20:0xBC]
    txt = s.split(b"\x00")[0]
    print("   str@20:", txt[:40])

for p,t in ((r"F:/sr2-cn/_fontdump/vf3_offi.bin","官方原版 N=2838"),
            (r"F:/sr2-cn/_fontdump/fnt_chinese.vf3_pc","当前游戏 N=2795")):
    hdr(open(p,"rb").read(), t)

print()
b = open(r"F:/sr2-cn/_fontdump/vf3_offi.bin","rb").read()
N=2838; H=0xBC; o=H+N*16
U = np.frombuffer(b,dtype="<u4",count=N,offset=o)
V = np.frombuffer(b,dtype="<u4",count=N,offset=o+N*4)
uu = sorted(set(U.tolist()))
print("官方 U 唯一值 %d 个, 前40:"%len(uu), uu[:40])
print("官方 U 唯一值 后20:", uu[-20:])
d = [uu[i+1]-uu[i] for i in range(len(uu)-1)]
from collections import Counter
print("官方 U 唯一值间距分布:", Counter(d).most_common(8))
vv = sorted(set(V.tolist()))
print("官方 V 唯一值 %d 个, 前12:"%len(vv), vv[:12], " 后6:", vv[-6:])
dv=[vv[i+1]-vv[i] for i in range(len(vv)-1)]
print("官方 V 间距分布:", Counter(dv).most_common(8))
