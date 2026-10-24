import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
p = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
v = Vpp(p)
t = v.read(v.find("charlist_CH","txt")).decode('utf-8', 'replace')
lines = t.split('\r\n') if '\r\n' in t else t.split('\n')
print("原始行数:", len(lines))
print("--- 前 8 行 ---")
for l in lines[:8]: print(repr(l))
print("--- 后 5 行 ---")
for l in lines[-5:]: print(repr(l))
nums = [int(s) for s in lines if s.strip().isdigit()]
print("数字条目数:", len(nums))
print("前 12 个:", nums[:12])
print("位置 365..380:", nums[365:381])
print("这些码点:", [hex(x) for x in nums[365:381]], [chr(x) if 32 <= x < 0x30000 else '?' for x in nums[365:381]])
# 找 你 U+4F60=20320
cp = 0x4F60
if cp in nums:
    i = nums.index(cp)
    print("\n你(U+4F60=20320) 位于第 %d 个条目(index=%d)" % (i, i))
else:
    print("\n!! 你 U+4F60 不在 charlist 中")
    print("   最接近的:", [ (x, abs(x-cp)) for x in nums if abs(x-cp) < 60 ][:10])
# 连续性
d = [nums[i+1]-nums[i] for i in range(len(nums)-1)]
from collections import Counter
print("\n相邻码点差分布:", Counter(d).most_common(8))
print("非1的位置示例:", [(i, nums[i], nums[i+1]) for i in range(len(nums)-1) if nums[i+1]-nums[i] != 1][:8])
