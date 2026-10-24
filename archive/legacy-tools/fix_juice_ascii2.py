"""修复第三方补丁的 ASCII 字形 —— 第二版（固定基线 + 严格 17x17 采样盒）。

第一版的问题
    1. 下划线 `_` 完全没画出来（它在基线下方，被裁掉了）
    2. 用「紧贴墨迹框再居中」会把每个字垂直位置弄乱，看起来不在一条基线上
    3. 绘制盒 18px > 引擎采样的 17px，右侧一列被削掉

本版做法
    * 用字体自身的 ascent/descent 计算基线，所有字形共用同一条基线
    * 只做水平 us 缩放（避免超出 17px 宽），不做垂直居中
    * 严格写进 (U, V) 起点的 17x17 区域，与引擎采样盒完全一致
"""
import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
OUTDIR = os.path.join(W, '_juice_fix', 'out')
os.makedirs(OUTDIR, exist_ok=True)

AW = AH = 2048
CELL = 17                    # 引擎采样盒宽度（vf3 width）
ROW_H = 28                   # RenderHeight
SS = 10
FONT = r'C:\Windows\Fonts\msyhbd.ttc'

v = Vpp(SRC)
atlas = np.frombuffer(v.read(v.find('fnt_chinese', 'g_peg_pc')), np.uint8).reshape(AH, AW).copy()
vf3 = bytes(v.read(v.find('fnt_chinese', 'vf3_pc')))
raw_cl = v.read(v.find('charlist_CH', 'txt')).decode('utf-8')
CPS = [int(l) for l in raw_cl.split('\n') if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
CH0 = 0xD0
U0 = CH0 + N * 16
U = list(struct.unpack_from('<%di' % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from('<%di' % nV, vf3, U0 + N * 4))
WID = [struct.unpack_from('<h', vf3, CH0 + i * 16)[0] for i in range(N)]

idx_of = {}
for i, cp in enumerate(CPS):
    if 0x20 <= cp <= 0x7E:
        idx_of.setdefault(cp, i)

# ---- 用字体度量确定基线 -------------------------------------------------
_ft = ImageFont.truetype(FONT, ROW_H * SS)
asc, desc = _ft.getmetrics()
print('字体 %s: ascent=%d descent=%d (在 %dpx 下)' % (FONT, asc, desc, ROW_H * SS))
# 渲染盒高度 = ROW_H*SS，基线放在 ascent 位置
BOXH = ROW_H * SS
BASE = asc


def render_row(s):
    """把字符串渲染成 (BOXH, 宽) 的灰度行，基线在 BASE。"""
    tmp = Image.new('L', (int(len(s) * ROW_H * SS * 1.2) + 40, BOXH + desc + 20), 0)
    ImageDraw.Draw(tmp).text((5, BASE), s, fill=255, font=_ft, anchor='ls')
    return np.asarray(tmp)


# 判定每字所需宽度：用字体 getlength
print()
print('=== 每字渲染宽度 vs vf3 width ===')
rows = []
for cp in range(0x20, 0x7F):
    i = idx_of.get(cp)
    if i is None:
        continue
    adv = _ft.getlength(chr(cp))
    rows.append((cp, i, adv, WID[i]))
for cp, i, adv, w in rows[:16]:
    print("  %-4r 索引 %-3d 字体宽度 %6.1f  vf3 width %d" % (chr(cp), i, adv, w))
print('  ...')
allw = [r[2] for r in rows]
print('  字体宽度范围 %.1f .. %.1f (均值 %.1f)；vf3 全部为 %d'
      % (min(allw), max(allw), sum(allw) / len(allw), rows[0][3]))

# ---- 逐字绘制 -----------------------------------------------------------
SCALE = 0.88                 # 稍微缩小，确保不超出单元
painted = 0
report = []
for cp in range(0x20, 0x7F):
    i = idx_of.get(cp)
    if i is None:
        continue
    x, y = U[i], V[i]
    y2, x2 = min(y + ROW_H, AH), min(x + CELL + 4, AW)
    atlas[y:y2, x:x2] = 0                       # 清空单元
    if cp == 0x20:
        report.append((' ', i, 0)); continue
    img = render_row(chr(cp))
    ys, xs = np.nonzero(img)
    if len(xs) == 0:
        report.append((chr(cp), i, 0)); continue
    # 水平范围 + 基线对齐：保留基线信息，不做垂直居中
    crop = img[:, xs.min():xs.max() + 1]
    hh, ww = crop.shape
    # 目标：宽度 <= CELL，且基线与 vf3 的 V 对齐
    scale = min(1.0, float(CELL) / ww) * SCALE + (1 - SCALE) * min(1.0, float(CELL) / ww)
    scale = min(1.0, float(CELL) / ww)
    nw = max(1, int(round(ww * scale)))
    nh = max(1, int(round(hh * scale)))
    small = np.asarray(Image.fromarray(crop).resize((nw, nh), Image.LANCZOS))
    # 基线下移量按同比例缩放
    base_new = int(round((BASE - ys.min()) * scale))
    tile = np.zeros((ROW_H, CELL), np.uint8)
    # 垂直放置：让基线落在 tile 内合适位置（与 V 起点对齐）
    top = base_new - int(round(BASE * scale))
    top = max(0, min(ROW_H - nh, top))
    left = max(0, min(CELL - nw, (CELL - nw) // 2))
    tile[top:top + min(nh, ROW_H - top), left:left + min(nw, CELL - left)] = \
        small[:min(nh, ROW_H - top), :min(nw, CELL - left)]
    h = min(ROW_H, y2 - y); w = min(CELL, x2 - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), i, int((tile > 24).sum())))
    painted += 1

empty = [ch for ch, i, ink in report if ink == 0 and ch != ' ']
print()
print('重绘 %d 个字形；无墨迹: %s' % (painted, ''.join(empty) if empty else '无'))

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
out = os.path.join(OUTDIR, 'patch.vpp_pc')
v2.save(out)
print('写出 %s (%d 字节)' % (out, os.path.getsize(out)))
