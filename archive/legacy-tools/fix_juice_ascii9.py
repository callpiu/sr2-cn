"""修复第三方补丁 ASCII 字形 —— 定版 4（用实测坐标）。

条带渲染实测（字号 18, 基线 70, 阈值 30）:
    A H W 0 Z 等大写/数字 : 行 56..69   (高 14)
    g p y                 : 行 60..74
    _                     : 行 73..74
    -                     : 行 64..65
    ,                     : 行 68..71
    .                     : 行 67..69

第三方图集实测目标:
    大写墨迹 行 9..22

=> 位移 DY = 9 - 56 = -47

先裁紧包围盒、再等比缩放，最后用「裁剪后墨迹顶边」定位，
顺序不能颠倒（上一版就是因为先缩放后裁剪，越界的墨迹被算进去了）。
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
FONT = r'C:\Windows\Fonts\msyhbd.ttc'
SIZE, STRIP_H, BASE, THR = 18, 100, 70, 30
TARGET_TOP, TARGET_CAP = 9, 14

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

# ---- 渲染条带 -----------------------------------------------------------
ft = ImageFont.truetype(FONT, SIZE)
SLOT = int(ft.getlength('W')) + 6
img = Image.new('L', (SLOT * 95, STRIP_H), 0)
dr = ImageDraw.Draw(img)
for k, cp in enumerate(range(0x20, 0x7F)):
    dr.text((k * SLOT + SLOT // 2, BASE), chr(cp), fill=255, font=ft, anchor='ms')
S = np.asarray(img)

# 大写顶边（用参考字符中位数）
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ct = []
for ch in REF:
    k = ord(ch) - 0x20
    ys = np.nonzero((S[:, k * SLOT:(k + 1) * SLOT] > THR).any(axis=1))[0]
    if len(ys):
        ct.append(int(ys.min()))
CT = int(np.median(ct))
DY = TARGET_TOP - CT
print('字号 %d, 槽宽 %d, 大写顶边 %d -> DY = %d' % (SIZE, SLOT, CT, DY))
print()

# ---- 逐字处理：先裁紧，再缩放，再用裁剪后顶边定位 ----------------------
atlas = A3.copy()
report = []
for cp in range(0x20, 0x7F):
    i = idx_of.get(cp)
    if i is None:
        continue
    x, y = U[i], V[i]
    ye, xe = min(y + ROW_H + 2, AH), min(x + 31, AW)
    atlas[y:ye, x:xe] = 0
    if cp == 0x20:
        report.append((' ', 0, None)); continue
    k = cp - 0x20
    sub = S[:, k * SLOT:(k + 1) * SLOT]
    ys, xs = np.nonzero(sub > THR)
    if len(xs) == 0:
        report.append((chr(cp), 0, None)); continue
    g = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]   # ★ 先裁紧
    gh, gw = g.shape
    # 再等比缩放到 28 行内、16px 宽内
    f = min(1.0, float(ROW_H) / gh, float(CELL - 1) / gw)
    if TARGET_CAP == 14 and abs(1.0 - f) < 1e-9:
        pass
    nh, nw = max(1, int(round(gh * f))), max(1, int(round(gw * f)))
    if (nh, nw) != (gh, gw):
        g = np.asarray(Image.fromarray(g).resize((nw, nh), Image.LANCZOS))
        gh, gw = g.shape
    tile = np.zeros((ROW_H, CELL), np.uint8)
    # 裁剪后该字墨迹顶 = 条带 ys.min()；相对大写顶的偏移 = ys.min() - CT
    top = TARGET_TOP + (int(ys.min()) - CT)
    left = max(0, (CELL - gw) // 2)
    for r in range(gh):
        tr = top + r
        if 0 <= tr < ROW_H:
            tile[tr, left:left + min(gw, CELL - left)] = g[r, :min(gw, CELL - left)]
    h = min(ROW_H, ye - y); w = min(CELL, xe - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), int((tile > 20).sum()), (top, top + gh - 1)))

empty = [ch for ch, ink, _ in report if ink == 0 and ch != ' ']
print('重绘 %d 个；无墨迹: %s' % (len([1 for c, k, _ in report if k > 0]),
                               ''.join(empty) if empty else '无'))
print()
print('=== 抽样：墨迹行范围（大写应 %d..%d）===' % (TARGET_TOP, TARGET_TOP + TARGET_CAP - 1))
for ch in "AHJgpy_0-=.W,;'":
    i = idx_of.get(ord(ch))
    if i is None:
        continue
    x, y = U[i], V[i]
    m = atlas[y:y + ROW_H, x:x + CELL] > 20
    ys2 = np.nonzero(m.any(axis=1))[0]
    print('  %-3r 行 %-10s 墨量 %d' % (ch, str((int(ys2.min()), int(ys2.max()))) if len(ys2) else '无', int(m.sum())))

v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
v2.save(OUT)
print()
print('写出 %s (%d 字节)' % (OUT, os.path.getsize(OUT)))
