"""修复第三方补丁 ASCII 字形 —— 简化定版。

最直白的做法：
    1. 用一个固定的超大字号把整个 95 个 ASCII 字符渲染到「一条 28 行高的条带」上
       —— 所有字符共享同一条基线，天然对齐
    2. 把这条带整体等比缩放，使大写字母高度 = 14px（第三方图集实测值）
    3. 缩放后把「大写字母墨迹顶边」对齐到行 9
    4. 逐字符裁出 17px 宽写进各自的 (U,V)

这样不需要逐字算基线，缩放在整条带上做，字符间相对位置一定正确。
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
SUPER = 16                     # 超采样字号基准
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

# ---- 实测目标 -----------------------------------------------------------
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
print('目标: 大写顶 %d 底 %d 高 %d px' % (TOP, BASE, CAP))

# ---- 1. 渲染整条带 -------------------------------------------------------
# 每个字符占一个槽位，槽宽按字体最大宽度；用一个大字号
FS = ROW_H * SUPER
ft = ImageFont.truetype(FONT, FS)
asc, desc = ft.getmetrics()
SLOT = int(ft.getlength('W')) + 8
STRIP_H = FS + desc + 40
BAND_Y = asc + 20                       # 条带内的基线 y
strip = Image.new('L', (SLOT * 95, STRIP_H), 0)
dr = ImageDraw.Draw(strip)
for k, cp in enumerate(range(0x20, 0x7F)):
    dr.text((k * SLOT + SLOT // 2, BAND_Y), chr(cp), fill=255, font=ft, anchor='ms')
S = np.asarray(strip)
print('条带 %dx%d, 基线 %d, 槽宽 %d' % (S.shape[1], S.shape[0], BAND_Y, SLOT))

# ---- 2. 量高度并缩放 -----------------------------------------------------
cap_h = []
for ch in REF:
    k = ord(ch) - 0x20
    sub = S[:, k * SLOT:(k + 1) * SLOT]
    ys = np.nonzero((sub > 24).any(axis=1))[0]
    if len(ys):
        cap_h.append(BAND_Y - int(ys.min()))
cap_h = float(np.median(cap_h))
scale = CAP / cap_h
nh = max(1, int(round(S.shape[0] * scale)))
nw_all = max(1, int(round(S.shape[1] * scale)))
S2 = np.asarray(Image.fromarray(S).resize((nw_all, nh), Image.LANCZOS))
band_y2 = int(round(BAND_Y * scale))
print('缩放 %.5f -> 条带 %dx%d, 基线 %d' % (scale, S2.shape[1], S2.shape[0], band_y2))

# 缩放后大写墨迹顶边在哪一行
cap_top2 = []
for ch in REF:
    k = ord(ch) - 0x20
    x0 = int(round(k * SLOT * scale)); x1 = min(S2.shape[1], int(round((k + 1) * SLOT * scale)))
    sub = S2[:, x0:x1]
    ys = np.nonzero((sub > 24).any(axis=1))[0]
    if len(ys):
        cap_top2.append(int(ys.min()))
cap_top2 = int(np.median(cap_top2))
DY = TOP - cap_top2                       # 需要的整体下移量
print('缩放后大写顶行 %d -> 需下移 %d 行使顶边落在 %d' % (cap_top2, DY, TOP))
print()

# ---- 3. 逐字写进图集 -----------------------------------------------------
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
    k = cp - 0x20
    x0 = int(round(k * SLOT * scale)); x1 = min(S2.shape[1], int(round((k + 1) * SLOT * scale)))
    sub = S2[:, x0:x1]
    ys, xs = np.nonzero(sub > 24)
    if len(xs) == 0:
        report.append((chr(cp), 0)); continue
    glyph = sub[:, xs.min():xs.max() + 1]
    gh, gw = glyph.shape
    tile = np.zeros((ROW_H, CELL), np.uint8)
    # 目标：该字形的墨迹顶边 = TOP + (该字墨迹顶 - 大写墨迹顶)
    top_target = TOP + (int(ys.min()) - cap_top2)
    left = max(0, (CELL - gw) // 2)
    for r in range(gh):
        tr = top_target + r
        if 0 <= tr < ROW_H:
            tile[tr, left:left + min(gw, CELL - left)] = glyph[r, :min(gw, CELL - left)]
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
