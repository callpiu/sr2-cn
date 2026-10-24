# -*- coding: utf-8 -*-
"""确定字节对齐：在 static_US 中搜索已知英文子串的位置，推算对齐与编码。"""
import os

M = r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods'
p = os.path.join(M, 'static_US.le_strings')
raw = open(p, 'rb').read()

# 已知英文子串
needles = [b'Your', b'the', b'You', b'Mission', b'Complete', b'Press', b'Health']
for nd in needles:
    idx = raw.find(nd)
    print('%-12s find=%s' % (nd.decode(), idx))
    if idx >= 0:
        print('   上下文 hex:', raw[max(0, idx - 8):idx + 16].hex())
        # 若为"字符+00"形态，会有 00 规律
print()
# 统计 00 的位置分布（奇/偶）
z_odd = sum(1 for i in range(1, len(raw), 2) if raw[i] == 0)
z_even = sum(1 for i in range(0, len(raw), 2) if raw[i] == 0)
print('00 @奇数位=%d  00 @偶数位=%d  (总数 %d)' % (z_odd, z_even, len(raw)))
