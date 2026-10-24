"""修复第三方补丁的 ASCII 字形 —— 定版。

最简可靠的对齐方式：
    第三方图集里，大写字母/数字的墨迹顶边在行 9、底边在行 22（实测中位数）。
    那么只要保证新字形的「大写墨迹顶边」落在行 9，
    「大写墨迹底边」自然落在行 22（因为高度已按同一比例缩放）。

    有下伸部的字符（g j p q y , _）的墨迹框比大写高，其底边按字体自身的
    下伸深度自然延伸到基线下，所以用「墨迹顶边 = TOP」统一对齐即可。
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

# ---- 实测目标：大写墨迹顶边 / 底边 --------------------------------------
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
tops, bots = [], []
for ch in REF:
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    ys = np.nonzero((A3[y:y + ROW_H, x:x + CELL] > 60).any(axis=1))[0]
    if len(ys):
        tops.append(int(ys.min())); bots.append(int(ys.max()))
TOP, BASE = int(np.median(tops)), int(np.median(bots))
CAP = BASE - TOP + 1
print('目标: 大写墨迹顶 %d, 底 %d, 高 %d px' % (TOP, BASE, CAP))

# ---- 渲染 ---------------------------------------------------------------
_ft = ImageFont.truetype(FONT, ROW_H * SS)
asc, desc = _ft.getmetrics()
CANVAS_H = ROW_H * SS + desc + 60
BASELINE_PX = asc
CW = int(_ft.getlength('W') * 3) + 40


def render(s):
    img = Image.new('L', (CW, CANVAS_H), 0)
    ImageDraw.Draw(img).text((10, BASELINE_PX), s, fill=255, font=_ft, anchor='ls')
    return np.asarray(img)


cap_px = []
for ch in REF:
    a = render(ch)
    ys = np.nonzero((a > 24).any(axis=1))[0]
    if len(ys):
        cap_px.append(BASELINE_PX - int(ys.min()))
cap_px = float(np.median(cap_px))
scale = CAP / cap_px
print('字体大写高度 %d px -> 缩放 %.4f' % (cap_px, scale))
print()

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
    sv = scale
    if nw > CELL - 1:
        f = float(CELL - 1) / nw
        nw, nh = CELL - 1, max(1, int(round(nh * f)))
        sv = scale * f
    small = np.asarray(Image.fromarray(crop).resize((nw, nh), Image.LANCZOS))
    # ★ 关键：该字符墨迹顶边相对「大写墨迹顶边」的差（超采样像素，向上为正）
    #   大写字符 top_rel = 0；下伸部字符的墨迹顶边也在同一位置（见下）
    #   用字体自身的 ascent 关系：墨迹顶边 = 该字符墨迹最高行
    top_rel = int(ys.min()) - int(min(
        np.nonzero((render(c) > 24).any(axis=1))[0].min() for c in REF))
    top = TOP + int(round(top_rel * sv))
    tile = np.zeros((ROW_H, CELL), np.uint8)
    left = max(0, (CELL - nw) // 2)
    for r in range(nh):
        tr = top + r
        if 0 <= tr < ROW_H:
            tile[tr, left:left + min(nw, CELL - left)] = \
                small[r, :min(nw, CELL - left)]
    h = min(ROW_H, ye - y); w = min(CELL, xe - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), int((tile > 24).sum())))

empty = [ch for ch, ink in report if ink == 0 and ch != ' ']
print('重绘 %d 个；无墨迹: %s' % (len([1 for c, k in report if k > 0]),
                               ''.join(empty) if empty else '无'))
print()
print('=== 抽样：墨迹行范围（大写应 %d..%d）===' % (TOP, BASE))
for ch in "AHJgpy_0-=.W,;":
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    m = atlas[y:y + ROW_H, x:x + CELL] > 24
    ys2 = np.nonzero(m.any(axis=1))[0]
    print('  %-3r 行 %-10s 墨量 %d' % (ch, str((int(ys2.min()), int(ys2.max()))) if len(ys2) else '无', int(m.sum())))

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
v2.save(OUT)
print()
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))
