# -*- coding: utf-8 -*-
"""全量校验：游戏当前加载的 static_CH.le_strings，
用 live charlist_CH(2795) 解码，统计「有多少条记录能解出合法文本」。
若绝大多数合法 → 数据侧完全自洽，乱码必来自运行时。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
cn = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8', 'replace').split('\n') if l.strip().isdigit()]
LE = len(cn)
raw = v.read(v.find('static_CH', 'le_strings'))
print('static_CH', len(raw), 'chars', LE)

# le_strings 结构：u32 count? 先探测。通常：文件头 = u32 magic/version, u32 num, 然后记录
print('head:', raw[:32].hex(' '))

# 尝试解析：常见 SR2 le_strings 结构 =
#   u32 count
#   然后 count 个 u32 (offset)  ...
# 先看前 16 个 u32
hdr = struct.unpack('<8I', raw[:32])
print('first 8 u32:', hdr)

# 统计整个文件里 u16 值的分布：若大量 slot 落在 [0x20, LE+0x20] 之外 → 说明不是这个表编码
import collections
vals = struct.unpack('<%dH' % (len(raw)//2), raw[:len(raw)//2*2])
inrange = sum(1 for x in vals if x == 0 or 0x20 <= x <= 0x7E or (0x20 <= x <= LE + 0x20))
print('u16 采样在合法范围的比例: %.3f (%d/%d)' % (inrange/len(vals), inrange, len(vals)))
mx = max(vals)
print('max u16 =', mx, hex(mx), ' LE+0x20 =', LE + 0x20)
over = sum(1 for x in vals if x > LE + 0x20)
print('超过 LE+0x20 的 u16 数量:', over)
