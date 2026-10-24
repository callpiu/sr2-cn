# -*- coding: utf-8 -*-
"""验证 charlist_CH.txt 的 ASCII 前缀到底多长。
关键：引擎 loadcharlist 是从 charlist 文本逐字符读，
      <0x100 的项 slot=codepoint；>=0x100 的项 slot=256+n。
所以「前缀长度」= 文本里连续出现 0x20..(0x20+k-1) 的个数。
"""
import sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
print("原始 token 数 =", len(ns))
print("前 5 个 =", ns[:5])
if ns and ns[0] == len(ns) - 1:
    print(">> 判定首项是计数，剥离")
    ns = ns[1:]
print("剥离后项数 =", len(ns))
print("前 12 项 =", [hex(x) for x in ns[:12]])
print("末 5 项  =", [hex(x) for x in ns[-5:]])

# 找连续升序 0x20.. 前缀
k = 0
expect = 0x20
for x in ns:
    if x == expect:
        k += 1; expect += 1
    else:
        break
print("\n=== 连续 ASCII 前缀长度 = %d (0x20..0x%02X) ===" % (k, 0x20+k-1))
print("第 %d 项起:", k, [hex(x) for x in ns[k:k+10]])

# 检查前 224 是不是 0x20..0xFF
if len(ns) >= 224:
    seg = ns[:224]
    ok = all(seg[i] == 0x20 + i for i in range(224))
    print("前 224 项 == 0x20..0xFF ?", ok)
    if not ok:
        bad = [(i, hex(seg[i])) for i in range(224) if seg[i] != 0x20+i][:10]
        print("  首个不符:", bad)

# 检查前 256
if len(ns) >= 256:
    seg = ns[:256]
    ok = all(seg[i] == 0x20 + i for i in range(256))
    print("前 256 项 == 0x20..0x11F ?", ok)
