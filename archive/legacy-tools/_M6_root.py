# -*- coding: utf-8 -*-
"""决定性验证：屏幕乱码 == 用 delta=0 解码正确文本 的结果？
若成立 → 根因 = 引擎/某处把 slot 当索引直接查表（少了 -32）
"""
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
CL=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]
cp2i={cp:i for i,cp in enumerate(CL)}

# 屏幕上看到的乱码
screen = "任璨偶巧位雄衡任璨伪该"
# 正确文本
correct = "你的弟兄们需要你的保护"

print("屏幕乱码:", screen)
print("正确文本:", correct)
print()
print("=== 假说: screen = ''.join(CL[slot - 0]) , 即 delta=0 ===")
out0=""
for ch in correct:
    i=cp2i.get(ord(ch))
    if i is None: 
        out0+='?'; continue
    slot=i+32
    out0 += chr(CL[slot]) if 0<=slot<len(CL) else '?'
print("  delta=0 解码正确文本 ->", out0)
print("  与屏幕乱码相同?", out0==screen)
print()
print("=== 逐字对照 (正确字 -> slot -> delta0字 / delta32字) ===")
for ch in correct:
    i=cp2i.get(ord(ch))
    if i is None: continue
    slot=i+32
    d0=chr(CL[slot]) if 0<=slot<len(CL) else '?'
    d32=chr(CL[slot-32]) if 0<=slot-32<len(CL) else '?'
    print("  %s(idx=%d slot=%d): delta0=%s  delta32=%s" % (ch,i,slot,d0,d32))
print()
# 另一个方向: 屏幕乱码字的索引 = ?
print("=== 屏幕乱码字的 CL 索引 ===")
for ch in screen:
    print("  %s idx=%s" % (ch, cp2i.get(ord(ch))))
