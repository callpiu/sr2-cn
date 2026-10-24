import sys, struct
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N=struct.unpack_from("<i",vf3,0x08)[0]
def rec(i):
    o=0xD0+i*16
    return struct.unpack_from("<iiii", vf3, o)
print("N =", N, " 记录区 0xD0..0x%X (共 %d 字节, %d 条×16B=%d)" % (0xD0+N*16, N*16, N, N*16))
print("U 数组起点 0xAF6C = %d,  记录区结束 0x%X = %d,  差 %d 字节 (%.2f 条)" % (0xAF6C,0xD0+N*16,0xD0+N*16, 0xAF6C-(0xD0+N*16), (0xAF6C-(0xD0+N*16))/16))
print()
print("%-5s %-4s %-10s %-10s %-10s %-10s" % ("idx","字","f0","f1","f2","f3"))
for i in (0,1,5,37,238,239,981,1025,1057,1190,1339,1764,2474):
    f=rec(i)
    print("%-5d %-4s %-10d %-10d %-10d %-10d" % (i, chr(CPS[i]), *f))
print()
# 检查 f1/f2 是否有规律
vals1=[rec(i)[1] for i in range(0,60)]
vals2=[rec(i)[2] for i in range(0,60)]
print("f1[0..20] =", vals1[:20])
print("f2[0..20] =", vals2[:20])
print("f1[235..245] =", [rec(i)[1] for i in range(235,246)])
print("f2[235..245] =", [rec(i)[2] for i in range(235,246)])
