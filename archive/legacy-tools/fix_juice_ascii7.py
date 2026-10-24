"""修复第三方补丁 ASCII 字形 —— 定版 2。

修正上一版的两个毛病
    1. 条带被缩到只剩 25 行，细笔画（, - . _ 等）抗锯齿后低于阈值 -> 整条消失
       => 改为在目标尺寸（28 行）直接渲染，不做大幅缩小
    2. 垂直位置靠推算，容易差几行
       => 直接从渲染条带上量「大写墨迹顶边」，再算位移量

做法
    * 字号 = 14px 大写高度对应的字号，直接渲染到 28 行高的条带（不缩放）
    * 量出条带内大写墨迹顶边 t，位移 DY = 9 - t
    * 逐字裁 17px 宽，贴到行 (DY + 该字墨迹顶)
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
TARGET_CAP = 14                 # 第三方图集实测的大写高度
TARGET_TOP = 9                  # 第三方图集实测的大写顶边行

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

# ---- 1. 找出「大写高度 = 14px」对应的字号 -------------------------------
REF = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def strip_for(size):
    ft = ImageFont.truetype(FONT, size)
    asc, desc = ft.getmetrics()
    slot = int(ft.getlength('W')) + 4
    H = asc + desc + 6 + 24
    img = Image.new('L', (slot * 95, H), 0)
    dr = ImageDraw.Draw(img)
    base = asc + 2 + 12
    for k, cp in enumerate(range(0x20, 0x7F)):
        dr.text((k * slot + slot // 2, base), chr(cp), fill=255, font=ft, anchor='ms')
    return np.asarray(img), slot, base, ft


best = None
for size in range(8, 40):
    S, slot, base, ft = strip_for(size)
    hs = []
    for ch in REF:
        k = ord(ch) - 0x20
        sub = S[:, k * slot:(k + 1) * slot]
        ys = np.nonzero((sub > 40).any(axis=1))[0]
        if len(ys):
            hs.append(base - int(ys.min()))
    if not hs:
        continue
    h = float(np.median(hs))
    if best is None or abs(h - TARGET_CAP) < abs(best[1] - TARGET_CAP):
        best = (size, h, S, slot, base, ft)
size, caph, S, SLOT, BASE, ft = best
print('选定字号 %d -> 大写高度 %.1f px (目标 %d)' % (size, caph, TARGET_CAP))
print('条带 %dx%d, 槽宽 %d, 基线 %d' % (S.shape[1], S.shape[0], SLOT, BASE))

cap_tops = []
for ch in REF:
    k = ord(ch) - 0x20
    sub = S[:, k * SLOT:(k + 1) * SLOT]
    ys = np.nonzero((sub > 40).any(axis=1))[0]
    if len(ys):
        cap_tops.append(int(ys.min()))
CT = int(np.median(cap_tops))
DY = TARGET_TOP - CT
print('条带内大写顶边 %d -> 位移 DY = %d' % (CT, DY))
print()

# ---- 2. 写进图集 --------------------------------------------------------
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
    ys, xs = np.nonzero(sub > 40)
    if len(xs) == 0:
        report.append((chr(cp), 0)); continue
    glyph = sub[:, xs.min():xs.max() + 1]
    gh, gw = glyph.shape
    if gw > CELL:                       # 水平压缩到 16px
        f = float(CELL - 1) / gw
        gw2 = CELL - 1
        gh2 = max(1, int(round(gh * f)))
        glyph = np.asarray(Image.fromarray(glyph).resize((gw2, gh2), Image.LANCZOS))
        gh, gw = glyph.shape
    tile = np.zeros((ROW_H, CELL), np.uint8)
    top = DY + int(ys.min())
    left = max(0, (CELL - gw) // 2)
    for r in range(gh):
        tr = top + r
        if 0 <= tr < ROW_H:
            tile[tr, left:left + min(gw, CELL - left)] = glyph[r, :min(gw, CELL - left)]
    h = min(ROW_H, ye - y); w = min(CELL, xe - x)
    atlas[y:y + h, x:x + w] = tile[:h, :w]
    report.append((chr(cp), int((tile > 24).sum())))

empty = [ch for ch, ink in report if ink == 0 and ch != ' ']
print('重绘 %d 个；无墨迹: %s' % (len([1 for c, k in report if k > 0]),
                               ''.join(empty) if empty else '无'))
print()
print('=== 抽样：墨迹行范围（大写应 %d..%d）===' % (TARGET_TOP, TARGET_TOP + TARGET_CAP - 1))
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
