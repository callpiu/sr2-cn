import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
vf3 = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
A = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
N = struct.unpack_from("<i",vf3,0x08)[0]
NK = struct.unpack_from("<i",vf3,0x20)[0]
# 记录区起点：文档说 0xC0；用文件大小反推
# 文件 = 0x28+0x40 + ... ; 试两种起点，看哪个让 U/V 落在合法范围
for CH0, tag in ((0xC0,"0xC0"), (0xD0,"0xD0")):
    U0 = CH0 + N*16
    try:
        U = list(struct.unpack_from("<%di"%N, vf3, U0))
        nV = (len(vf3)-(U0+N*4))//4
        V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
        ok = sum(1 for x in U if 0 <= x < 2048)
        print("起点 %s: 记录区 %d..%d, U 区 %d, U 合法个数 %d/%d, V 个数 %d" % (
            tag, CH0, U0, U0, ok, N, nV))
    except Exception as e:
        print("起点 %s 失败: %s" % (tag, e))
