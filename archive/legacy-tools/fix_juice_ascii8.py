"""修复第三方补丁 ASCII 字形 —— 定版 3（一次写对）。

踩过的坑
    1. 条带太矮 -> 下伸部被裁 -> 量出的墨迹顶边错 -> 整体下移
    2. 条带缩小太多 -> 细笔画（, - . _）抗锯齿后低于阈值 -> 整条消失

本版
    * 条带高度 100 行，基线放 70 —— 上下都留足余量，绝不裁切
    * 字号搜索：找「大写高度 = 14px」的字号
    * 位移 DY = 9 - 条带内大写墨迹顶边
    * 每字墨迹顶边用条带内的真实测量值（不推算）
    * 只在最后粘贴进 28 行 tile 时裁切
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
TARGET_CAP, TARGET_TOP = 14, 9
STRIP_H, BASELINE = 100, 70
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
THR = 30

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


def build(size):
    ft = ImageFont.truetype(FONT, size)
    slot = int(ft.getlength('W')) + 6
    img = Image.new('L', (slot * 95, STRIP_H), 0)
    dr = ImageDraw.Draw(img)
    for k, cp in enumerate(range(0x20, 0x7F)):
        dr.text((k * slot + slot // 2, BASELINE), chr(cp), fill=255, font=ft, anchor='ms')
    return np.asarray(img), slot


# ---- 选字号：大写高度最接近 14 -----------------------------------------
best = None
for size in range(8, 44):
    S, slot = build(size)
    hs = []
    for ch in REF:
        k = ord(ch) - 0x20
        ys = np.nonzero((S[:, k * slot:(k + 1) * slot] > THR).any(axis=1))[0]
        if len(ys):
            hs.append(BASELINE - int(ys.min()))
    if not hs:
        continue
    h = float(np.median(hs))
    if best is None or abs(h - TARGET_CAP) < abs(best[1] - TARGET_CAP):
        best = (size, h, S, slot)
size, caph, S, SLOT = best
print('字号 %d -> 大写高度 %.1f px (目标 %d), 条带 %dx%d, 槽宽 %d'
      % (size, caph, TARGET_CAP, S.shape[1], S.shape[0], SLOT))

cap_tops = []
for ch in REF:
    k = ord(ch) - 0x20
    ys = np.nonzero((S[:, k * SLOT:(k + 1) * SLOT] > THR).any(axis=1))[0]
    if len(ys):
        cap_tops.append(int(ys.min()))
CT = int(np.median(cap_tops))
DY = TARGET_TOP - CT
print('条带内大写顶边 %d -> DY = %d' % (CT, DY))
print()

# ---- 写进图集 ----------------------------------------------------------
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
    sub = S[:, k * SLOT:(k + 1) * SLOT]
    ys, xs = np.nonzero(sub > THR)
    if len(xs) == 0:
        report.append((chr(cp), 0)); continue
    g = sub[:, xs.min():xs.max() + 1]
    gh, gw = g.shape
    if gw > CELL - 1:
        f = float(CELL - 1) / gw
        gw2, gh2 = CELL - 1, max(1, int(round(gh * f)))
        g = np.asarray(Image.fromarray(g).resize((gw2, gh2), Image.LANCZOS))
        gh, gw = g.shape
    tile = np.zeros((ROW_H, CELL), np.uint8)
    top = DY + int(ys.min())
    left = max(0, (CELL - gw) // 2)
    for r in range(gh):
        tr = top + r
        if 0 <= tr < ROW_H:
            tile[tr, left:left + min(gw, CELL - left)] = g[r, :min(gw, CELL - left)]
    h = min(ROW_H, ye - y); w = min(CELL, xe - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), int((tile > 20).sum())))

empty = [ch for ch, ink in report if ink == 0 and ch != ' ']
print('重绘 %d 个；无墨迹: %s' % (len([1 for c, k in report if k > 0]),
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
