import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
T = 0x69AD7
# 从 T 开始向后解到 00 00
out=[]
j = T
while j < len(d)-1:
    x = struct.unpack_from("<H", d, j)[0]
    if x == 0: break
    out.append(S.get(x, "\uFFFD"))
    j += 2
print("=== 从 丈王 开始向后解出的文本 ===")
print("".join(out))
print()
# 从 T 向前解（找这条记录的文本起点）：向前直到遇到 00 00 或非文本
pre=[]
j = T-2
while j > 0:
    x = struct.unpack_from("<H", d, j)[0]
    if x == 0: break
    pre.append(S.get(x, "\uFFFD"))
    j -= 2
pre.reverse()
print("=== 向前解出（文本前半）===")
print("".join(pre))
print()
print("=== 完整记录（向前+向后）===")
full = "".join(pre) + "".join(out)
print(full)
print()
print("长度 %d 字符" % len(full))
print()
# 在整条里找「三」或「丈」
for k,ch in enumerate(full):
    if ch in "三丈王":
        print("  位置 %d: %r  上下文: %r" % (k, ch, full[max(0,k-12):k+12]))
