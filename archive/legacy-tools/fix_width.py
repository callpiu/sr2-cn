"""修复第三方字体：ASCII 的 width 字段（= 字符步进的来源）。

诊断（全部实测）
    1. 引擎的字符步进 = width + CharSpacing
       原厂: 18 + (-5) = 13px —— 与图集实际排布一致
       第三方: 17 + (-5) = 12px —— 但字形实际宽约 36px

    2. 第三方 ASCII 字形在 U 起点后第 3..39 列有墨迹 => 实际宽约 36px
       所以 12px 步进让相邻字重叠挤压，笔画互相覆盖 -> 看起来「缺字」

    3. 图集本身完好（DXT3 解码后 95 个 ASCII 字形全部清晰）
       字形位置也对（墨迹就落在各自的 (U,V) 处）

修复
    把 ASCII（索引 0..94）的 width 从 17 改成 40：
        步进 = 40 + (-5) = 35px  ≈ 字形实际宽度
    只改 width 字段，不动 U/V、不动图集、不动文本。

    同时把 CJK 区（索引 95+）的 width 也按同样比例放大，
    让整个字体步进一致（CJK 也偏小，同样会被挤压）。
"""
import sys, os, struct
import numpy as np

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp, dxt3_decode

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
OUT = os.path.join(W, '_juice_fix', 'out2', 'patch.vpp_pc')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

v = Vpp(SRC)
_, al = dxt3_decode(bytes(v.read(v.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
vf3 = bytearray(v.read(v.find('fnt_chinese', 'vf3_pc')))
CPS = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n')
       if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
CH0 = 0xD0
U0 = CH0 + N * 16
U = list(struct.unpack_from('<%di' % N, vf3, U0))
CHARSP = struct.unpack_from('<i', vf3, 0x1C)[0]
print('N=%d  CharSpacing=%d' % (N, CHARSP))

# ---- 实测每个字形的墨迹宽度（相对 U 的列范围）----
print()
print('=== 实测字形宽度（取每区中位数）===')


def span(i, win):
    """返回该字形相对 U 的墨迹列范围 (first, last)。"""
    u = U[i]
    if u < 0 or u >= 2048:
        return None
    seg = al[1:29, u:min(u + win, 2048)] > 32
    c = np.nonzero(seg.any(axis=0))[0]
    if not len(c):
        return None
    return int(c.min()), int(c.max())


ascii_spans, cjk_spans = [], []
for i in range(N):
    win = 45 if i < 95 else 34
    s = span(i, win)
    if s is None:
        continue
    (ascii_spans if i < 95 else cjk_spans).append(s)
a_first = int(np.median([a for a, b in ascii_spans]))
a_last = int(np.median([b for a, b in ascii_spans]))
c_first = int(np.median([a for a, b in cjk_spans]))
c_last = int(np.median([b for a, b in cjk_spans]))
print('  ASCII: 墨迹列 %d..%d  -> 实际宽 %d  (记录 width=17, 步进=%d)'
      % (a_first, a_last, a_last - a_first + 1, 17 + CHARSP))
print('  CJK  : 墨迹列 %d..%d  -> 实际宽 %d' % (c_first, c_last, c_last - c_first + 1))

# 目标步进 = 实际墨迹宽度 + 1px 余量
a_target = a_last - a_first + 2
c_target = c_last - c_first + 2
a_width = a_target - CHARSP
c_width = c_target - CHARSP
print()
print('目标: ASCII 步进 %d -> width %d ; CJK 步进 %d -> width %d'
      % (a_target, a_width, c_target, c_width))

# ---- 写回 width（+0x00 和 +0x0C 两处）----
changed_ascii = changed_cjk = 0
for i in range(N):
    off = CH0 + i * 16
    old = struct.unpack_from('<h', vf3, off)[0]
    new = a_width if i < 95 else c_width
    if old == new:
        continue
    struct.pack_into('<h', vf3, off, new)
    struct.pack_into('<h', vf3, off + 12, new)
    if i < 95:
        changed_ascii += 1
    else:
        changed_cjk += 1
print()
print('改写 width: ASCII %d 个, CJK %d 个' % (changed_ascii, changed_cjk))

# ---- 注意：不要再缩短 U 数组长度（不能改变文件结构）----
assert len(vf3) == 67268, len(vf3)

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'vf3_pc'), bytes(vf3))
v2.save(OUT)
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))

# ---- 复验 ----
chk = Vpp(OUT)
nv = chk.read(chk.find('fnt_chinese', 'vf3_pc'))
print()
print('复验: vf3 %d 字节 (应 67268)' % len(nv))
for i in (0, 1, 33, 36, 78, 83, 100, 500):
    r = struct.unpack_from('<8h', nv, CH0 + i * 16)
    print('  索引 %-4d width=%d  字符 %s' % (i, r[0], chr(CPS[i])))
