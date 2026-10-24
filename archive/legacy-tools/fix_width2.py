"""修复第三方字体 ASCII 区的 width 字段。

实测数据
    图集里 ASCII 字形: 每个格子步距 31px，格内墨迹宽约 9px（列 3..11）
    但 vf3 记录 width = 17，且引擎的字符步进 = width + CharSpacing

    原厂繁中做对照:
        width = 18, CharSpacing = -5  ->  步进 13px
        而原厂图集 ASCII 墨迹宽约 30px
        => 原厂的「步进 13px」也一样小于「墨迹 30px」
        => 说明步进与墨迹宽度本来就不同量纲，不能用墨迹宽度反推 width

本次采取最小改动
    ASCII 区 width: 17 -> 31（等于图集的格距）
    只改 ASCII，CJK 保持原样（CJK 在原厂就是 30，第三方的 30 是对的）
    不动 U/V、不动图集、不动文本
"""
import sys, os, struct

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
OUT = os.path.join(W, '_juice_fix', 'out3', 'patch.vpp_pc')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

v = Vpp(SRC)
vf3 = bytearray(v.read(v.find('fnt_chinese', 'vf3_pc')))
CPS = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n')
       if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
CH0 = 0xD0

# 原始值分布（先看清楚）
import collections
dist = collections.Counter()
for i in range(N):
    dist[struct.unpack_from('<h', vf3, CH0 + i * 16)[0]] += 1
print('改前 width 分布: %s' % dict(dist.most_common(8)))

NEW_ASCII = 31
n = 0
for i in range(95):
    off = CH0 + i * 16
    if struct.unpack_from('<h', vf3, off)[0] != NEW_ASCII:
        struct.pack_into('<h', vf3, off, NEW_ASCII)
        struct.pack_into('<h', vf3, off + 12, NEW_ASCII)
        n += 1
print('ASCII width 改成 %d: %d 个' % (NEW_ASCII, n))

assert len(vf3) == 67268

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'vf3_pc'), bytes(vf3))
v2.save(OUT)
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))

# 与第三方原版逐条比对，确认只动了 vf3
v0 = Vpp(SRC)
vn = Vpp(OUT)
diff = []
for e in v0.entries():
    e2 = vn.find(e['name'], e['ext']) if e['ext'] else None
    if e2 is None:
        continue
    if v0.read(e) != vn.read(e2):
        diff.append('%s.%s' % (e['name'], e['ext']))
print('内容不同的资源: %s' % diff)
