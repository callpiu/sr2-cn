import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("charlist_CH", "txt")
b = v.read(e)
print("size", len(b))
print("head:", b[:180])
nums = [int(x) for x in re.findall(rb'\d+', b)]
print("count parsed =", len(nums), " first20 =", nums[:20])
have = set(nums)
for c in "ABCabc0123 .,!?-":
    print(f"  {c!r} U+{ord(c):04X} in list? {ord(c) in have}")
# 统计 CJK 区间
cjk = sum(1 for n in nums if 0x4E00 <= n <= 0x9FFF)
print("CJK 4E00-9FFF count =", cjk)
