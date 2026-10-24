"""修复第三方补丁的 ASCII 字形 —— 第三版（从原始第三方图集测基线）。

思路
    第三方图集的 ASCII 位图虽然糊，但「基线的纵向位置」还能测出来。
    1. 从原始第三方图集量出「数字/大写字母」墨迹底边的中位数 = 基线 B
    2. 用系统字体把每个字符渲染到 28 行高的条带里，让墨迹底边落在 B
       （有下伸部的字符 g/y/p/q/j/,_ 按其下伸深度自然低于 B）
    3. 水平方向压进 17px 采样盒
    4. 写回 (U, V) 起点的 17x28 区域

这样既保持基线一致，又不会裁掉下划线。
"""
import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')       # 第三方原始
OUT = os.path.join(W, '_juice_fix', 'out', 'patch.vpp_pc')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

AW = AH = 2048
CELL, ROW_H = 17, 28
SS = 10
FONT = r'C:\Windows\Fonts\msyhbd.ttc'

v = Vpp(SRC)
A3 = np.frombuffer(v.read(v.find('fnt_chinese', 'g_peg_pc')), np.uint8).reshape(AH, AW)
vf3 = bytes(v.read(v.find('fnt_chinese', 'vf3_pc')))
raw_cl = v.read(v.find('charlist_CH', 'txt')).decode('utf-8')
CPS = [int(l) for l in raw_cl.split('\n') if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from('<%di' % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from('<%di' % nV, vf3, U0 + N * 4))
idx_of = {}
for i, cp in enumerate(CPS):
    if 0x20 <= cp <= 0x7E:
        idx_of.setdefault(cp, i)

# ---- 1. 从原始第三方图集测基线 ------------------------------------------
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
bottoms, tops = [], []
for ch in REF:
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    blk = A3[y:y + ROW_H, x:x + CELL]
    m = blk > 60
    ys = np.nonzero(m.any(axis=1))[0]
    if len(ys):
        tops.append(int(ys.min()))
        bottoms.append(int(ys.max()))
BASE = int(np.median(bottoms)) if bottoms else 19
TOP = int(np.median(tops)) if tops else 3
print('第三方图集实测: 大写/数字 墨迹顶边中位数 %d, 底边中位数 %d (即基线)' % (TOP, BASE))
print('  -> 字高约 %d 像素 (vf3 RenderHeight=%d)' % (BASE - TOP + 1, ROW_H))

# ---- 2. 用字体渲染，令墨迹底边落在 BASE ---------------------------------
_ft = ImageFont.truetype(FONT, ROW_H * SS)
asc, desc = _ft.getmetrics()
CANVAS_H = ROW_H * SS + desc + 40
BASE_PX = asc            # 画布里的基线位置


def render(ch):
    tmp = Image.new('L', (ROW_H * SS * 2, CANVAS_H), 0)
    ImageDraw.Draw(tmp).text((ROW_H * SS // 2, BASE_PX), ch, fill=255, font=_ft, anchor='ms')
    return np.asarray(tmp)


# 先测一批参考字符在画布里的墨迹底边，换算缩放
ref_bottoms = []
for ch in REF:
    a = render(ch)
    ys = np.nonzero((a > 24).any(axis=1))[0]
    if len(ys):
        ref_bottoms.append(int(ys.max()))
cap_px = int(np.median(ref_bottoms)) - BASE_PX     # 大写字母在基线上方的高度（超采样像素）
scale = (BASE - TOP + 1) / float(max(1, cap_px))
print('  字体大写高度 %d 超采样像素 -> 缩放系数 %.4f' % (cap_px, scale))
print()

# ---- 3. 绘制 ------------------------------------------------------------
atlas = A3.copy()
painted, report = 0, []
for cp in range(0x20, 0x7F):
    i = idx_of.get(cp)
    if i is None:
        continue
    x, y = U[i], V[i]
    ye, xe = min(y + ROW_H, AH), min(x + CELL + 6, AW)
    atlas[y:ye, x:xe] = 0
    if cp == 0x20:
        report.append((' ', 0)); continue
    a = render(chr(cp))
    ys, xs = np.nonzero(a > 24)
    if len(xs) == 0:
        report.append((chr(cp), 0)); continue
    # 只取墨迹所在列，垂直方向保留整条（含下伸部）
    crop = a[:, xs.min():xs.max() + 1].astype(np.float32)
    hh, ww = crop.shape
    nw = max(1, min(CELL - 1, int(round(ww * scale))))
    nh = max(1, int(round(hh * scale)))
    small = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize((nw, nh), Image.LANCZOS))
    # 画布里的基线映射到 tile 里的 BASE
    base_new = int(round(BASE_PX * scale))
    top = BASE - base_new
    tile = np.zeros((ROW_H, CELL), np.uint8)
    left = max(0, (CELL - nw) // 2)
    for r in range(nh):
        tr = top + r
        if not (0 <= tr < ROW_H):
            continue
        for c in range(nw):
            tc = left + c
            if 0 <= tc < CELL:
                tile[tr, tc] = small[r, c]
    h = min(ROW_H, ye - y); w = min(CELL, xe - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), int((tile > 24).sum())))
    painted += 1

empty = [ch for ch, ink in report if ink == 0 and ch != ' ']
print('重绘 %d 个字形；无墨迹: %s' % (painted, ''.join(empty) if empty else '无'))
# 抽样看基线
print()
print('=== 抽样墨迹行范围（应在 %d..%d 之间一致）===' % (TOP, BASE))
for ch in "AJgpy_0-=":
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    m = atlas[y:y + ROW_H, x:x + CELL] > 24
    ys = np.nonzero(m.any(axis=1))[0]
    print('  %-3r 行 %s' % (ch, (int(ys.min()), int(ys.max())) if len(ys) else '无'))

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
v2.save(OUT)
print()
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))
