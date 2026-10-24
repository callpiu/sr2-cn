import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
nums = [int(s) for s in t if s.strip().isdigit()]
SENT = [0x4F60,0x7684,0x5F1F,0x5144,0x4EEC,0x9700,0x8981,0x4F60,0x7684,0x4FDD,0x62A4]
disp=[]
for cp in SENT:
    idx = nums.index(cp)
    g = idx + 32                      # cc_list 的 glyph 字段
    shown = nums[g] if g < len(nums) else None
    d = chr(shown) if shown and 32<=shown<0x30000 else '(越界%s)'%g
    disp.append(d)
    print("U+%04X idx=%4d glyph=%4d -> 第%4d格 = %s" % (cp, idx, g, g, d))
print()
print("引擎按 glyph 直取图集会显示:", "".join(disp))
