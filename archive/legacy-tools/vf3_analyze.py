import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
print("NumCharacters = %d, 字表 %d" % (N, len(CPS)))
print()
# 检查 U/V 数组是否可能起始位置不同
# 记录区 0xD0 + N*16 = 0xD0 + 2795*16 = %d
U0 = 0xD0 + N*16
print("记录区结束 = 0x%X (%d)" % (U0, U0))
print("文件大小 = %d" % len(vf3))
print("U 数组(假设 N 项) = %d 字节 -> 结束于 %d" % (N*4, U0+N*4))
print("V 数组剩余 = %d 字节 = %d 项" % (len(vf3)-(U0+N*4), (len(vf3)-(U0+N*4))//4))
print()
# 打印 U 数组的开头/结尾，以及 V 数组的开头，看是否合理
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV = (len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
print("U[0:8]   = %s" % U[:8])
print("U[-8:]   = %s" % U[-8:])
print("V[0:8]   = %s" % V[:8])
print("V[-8:]   = %s" % V[-8:])
print()
print("U 的分布: min=%d max=%d  %d 项在 0..2048 外" % (min(U), max(U), sum(1 for x in U if not (0<=x<2048))))
print("V 的分布: min=%d max=%d  %d 项在 0..2048 外" % (min(V), max(V), sum(1 for x in V if not (0<=x<2048))))
print()
# 关键：U/V 是否单调？如果不是，可能读取位置错了
mono = sum(1 for i in range(1,N) if U[i] >= U[i-1])
print("U 递增的位置数: %d / %d" % (mono, N-1))
print()
# 看看 U 的前 40 项
print("U[0:40] = %s" % U[:40])
