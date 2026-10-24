"""修复第三方补丁的 ASCII 字形 —— 第四版。

修正前三版的错误
    v1: 用「紧贴墨迹框再居中」-> 基线不一致；`_` 被裁掉
    v2/v3: ImageDraw 的 anchor='ms' 把基准点放在墨迹正下方，导致只画出顶端几条线

本版做法
    1. 在一个足够大的画布上，用 anchor='ls'（左-基线）把字符画在已知基线位置
    2. 从画布里量出墨迹的真实 bounding box
    3. 按比例缩放，使「大写字母高度」等于从原始第三方图集实测的字高
    4. 让墨迹底边（大写字母的）落在实测基线上；有下伸部的字符自然更低
    5. 水平压进 17px 采样盒，垂直写进 28 行
"""
import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
OUT = os.path.join(W, '_juice_fix', 'out', 'patch.vpp_pc')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

AW = AH = 2048
CELL, ROW_H = 17, 28
SS = 12
FONT = r'C:\Windows\Fonts\msyhbd.ttc'

v = Vpp(SRC)
A3 = np.frombuffer(v.read(v.find('fnt_chinese', 'g_peg_pc')), np.uint8).reshape(AH, AW)
vf3 = bytes(v.read(v.find('fnt_chinese', 'vf3_pc')))
CPS = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n')
       if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from('<%di' % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from('<%di' % nV, vf3, U0 + N * 4))
idx_of = {}
for i, cp in enumerate(CPS):
    if 0x20 <= cp <= 0x7E:
        idx_of.setdefault(cp, i)

# ---- 1. 从原始第三方图集测字高与基线（只统计大写/数字，避免受下伸部影响）----
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
tops, bots = [], []
for ch in REF:
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    blk = A3[y:y + ROW_H, x:x + CELL]
    ys = np.nonzero((blk > 60).any(axis=1))[0]
    if len(ys):
        tops.append(int(ys.min())); bots.append(int(ys.max()))
TOP, BASE = int(np.median(tops)), int(np.median(bots))
CAP = BASE - TOP + 1
print('第三方图集实测: 大写墨迹 顶 %d 底 %d -> 字高 %d px' % (TOP, BASE, CAP))

# ---- 2. 渲染函数（anchor='ls' 左-基线）----
_ft = ImageFont.truetype(FONT, ROW_H * SS)
asc, desc = _ft.getmetrics()
CANVAS_H = ROW_H * SS + desc + 60
BASELINE_PX = asc
CW = int(_ft.getlength('W') * 3) + 40


def render(ch):
    img = Image.new('L', (CW, CANVAS_H), 0)
    ImageDraw.Draw(img).text((10, BASELINE_PX), ch, fill=255, font=_ft, anchor='ls')
    return np.asarray(img)


# 量出字体自身的大写高度（超采样像素）
caps = []
for ch in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    a = render(ch)
    ys = np.nonzero((a > 24).any(axis=1))[0]
    if len(ys):
        caps.append(BASELINE_PX - int(ys.min()))
cap_px = float(np.median(caps))
scale = CAP / cap_px
print('字体大写高度 %d 超采样像素 -> 缩放 %.4f' % (cap_px, scale))
print('画布 %dx%d, 基线 %d' % (CW, CANVAS_H, BASELINE_PX))
print()

# ---- 3. 绘制 ------------------------------------------------------------
atlas = A3.copy()
report = []
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
    crop = a[:, xs.min():xs.max() + 1]
    hh, ww = crop.shape
    nw = max(1, int(round(ww * scale)))
    nh = max(1, int(round(hh * scale)))
    # 水平只压缩、不放大超过 16px
    if nw > CELL - 1:
        f = float(CELL - 1) / nw
        nw = CELL - 1
        nh = max(1, int(round(nh * f)))
        scale_v = scale * f
    else:
        scale_v = scale
    small = np.asarray(Image.fromarray(crop).resize((nw, nh), Image.LANCZOS))
    # 该字符墨迹底边相对基线的位置（超采样像素，正=在基线上方）
    bottom_rel = BASELINE_PX - int(ys.max())
    bottom_tile = BASE + int(round(bottom_rel * scale_v)) - int(round(cap_px*scale_v))
    top = bottom_tile - nh + 1
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

empty = [ch for ch, ink in report if ink == 0 and ch != ' ']
ok = [ch for ch, ink in report if ink > 0]
print('重绘成功 %d 个；无墨迹 %d 个: %s' % (len(ok), len(empty), ''.join(empty)))

print()
print('=== 抽样：墨迹行范围（大写应约 %d..%d）===' % (TOP, BASE))
for ch in "AHJgpy_0-=.W":
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    m = atlas[y:y + ROW_H, x:x + CELL] > 24
    ys2 = np.nonzero(m.any(axis=1))[0]
    print('  %-3r 行 %-10s 墨量 %d' % (ch, str((int(ys2.min()), int(ys2.max()))) if len(ys2) else '无',
                                    int(m.sum())))

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
v2.save(OUT)
print()
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))
