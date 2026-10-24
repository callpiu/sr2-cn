"""修复第三方补丁的 ASCII 字形（Juice 菜单缺字母的根因）。

诊断结论
    第三方 patch.vpp_pc 的 fnt_chinese.g_peg_pc（2048x2048 原始 8bit 灰度）
    在 ASCII 区（字符 0x20..0x7E）的字形位图已损坏 —— 全是噪点横纹，
    一个字母都认不出。CJK 区同样损坏。

    这不是「字距错乱」（旧文档 4.4 节的结论有误），而是位图本身坏了。
    Juice 菜单的英文标签走 ASCII 区，所以缺字母最明显。

修复方案
    保留第三方的 charlist / vf3 / 文本（文本索引与字符对应关系不变），
    只把 ASCII 区的 95 个字形用系统字体重绘到 vf3 给出的 (U,V) 坐标。

    这样 Juice 菜单的英文字母恢复正常，且不触碰任何索引。
"""
import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp, dxt3_decode

W = r'F:\sr2-cn'
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
OUTDIR = os.path.join(W, '_juice_fix', 'out')
os.makedirs(OUTDIR, exist_ok=True)

AW = AH = 2048
SHIFT = 0x20
SS = 8                      # 超采样倍数
FONT_CANDIDATES = [
    (r'C:\Windows\Fonts\msyhbd.ttc', 'Microsoft YaHei Bold'),
    (r'C:\Windows\Fonts\msyh.ttc', 'Microsoft YaHei'),
    (r'C:\Windows\Fonts\arialbd.ttf', 'Arial Bold'),
    (r'C:\Windows\Fonts\arial.ttf', 'Arial'),
]

# ---------- 1. 读入第三方资源 ----------
v = Vpp(SRC)
ent_atlas = v.find('fnt_chinese', 'g_peg_pc')
ent_vf3 = v.find('fnt_chinese', 'vf3_pc')
ent_cl = v.find('charlist_CH', 'txt')
assert ent_atlas and ent_vf3 and ent_cl, '资源未找到'

atlas = np.frombuffer(v.read(ent_atlas), np.uint8).reshape(AH, AW).copy()
vf3 = bytearray(v.read(ent_vf3))
raw_cl = v.read(ent_cl).decode('utf-8')
CPS = [int(l) for l in raw_cl.split('\n') if l.strip().isdigit()]
N = struct.unpack_from('<i', vf3, 0x08)[0]
NK = struct.unpack_from('<i', vf3, 0x20)[0]
CH0 = 0xD0 + NK * 12
U0 = CH0 + N * 16
U = list(struct.unpack_from('<%di' % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from('<%di' % nV, vf3, U0 + N * 4))
WID = [struct.unpack_from('<h', vf3, CH0 + i * 16)[0] for i in range(N)]
print('第三方: charlist %d 项, vf3 NumChars %d, 记录区起点 0x%X' % (len(CPS), N, CH0))

# ---------- 2. 建立「字符 -> 索引」映射 ----------
# 第三方 charlist 前 95 项就是 0x20..0x7E，但为稳妥起见按实际码点查
idx_of = {}
for i, cp in enumerate(CPS):
    if 0x20 <= cp <= 0x7E:
        idx_of.setdefault(cp, i)

# 实测每个 ASCII 字形的实际墨迹框（用于确认宽度体系）
print()
print('=== ASCII 前 12 项的 vf3 数据 ===')
for cp in range(0x20, 0x2C):
    i = idx_of.get(cp)
    if i is None:
        continue
    print("  %-4r 索引 %3d  (U=%4d, V=%3d)  width=%2d" % (chr(cp), i, U[i], V[i], WID[i]))

# ---------- 3. 用系统字体渲染 ASCII 字形 ----------
font_path, font_name = None, None
for p, n in FONT_CANDIDATES:
    if os.path.exists(p):
        font_path, font_name = p, n
        break
assert font_path, '找不到可用字体'
print()
print('使用字体: %s (%s)' % (font_path, font_name))

BOX = 18                     # 绘制盒（略大于 17 的标称宽度，留出抗锯齿余量）
_ft = ImageFont.truetype(font_path, BOX * SS)


def render(ch):
    """把一个字符渲染成 BOX x BOX 的 8bit 灰度图（已归一化到黑底白字）。"""
    big = BOX * SS
    t = Image.new('L', (big, big), 0)
    ImageDraw.Draw(t).text((big // 2, big // 2), ch, fill=255, font=_ft, anchor='mm')
    a = np.asarray(t)
    m = a > 24
    if m.sum() < 10:
        return np.zeros((BOX, BOX), np.uint8)
    ys, xs = np.nonzero(m)
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hh, ww = crop.shape
    # 缩放到 BOX-1 以内，保持比例
    sc = float(BOX - 1) / max(hh, ww)
    nw, nh = max(1, int(round(ww * sc))), max(1, int(round(hh * sc)))
    crop = np.asarray(Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)).astype(np.float32)
    x = np.clip(crop / 255.0, 0, 1)
    # 提高对比度，让细笔画在 17px 下仍可见
    x = np.clip((x - 0.25) / (0.75 - 0.25), 0, 1)
    x = x * x * (3 - 2 * x)
    crop = (x * 255).astype(np.uint8)
    tile = np.zeros((BOX, BOX), np.uint8)
    oy, ox = (BOX - nh) // 2, (BOX - nw) // 2
    tile[oy:oy + nh, ox:ox + nw] = crop
    return tile


# ---------- 4. 写入图集 ----------
# 先清空旧的 ASCII 单元区域（避免残留噪点）
CELL = 34
painted = 0
report = []
for cp in range(0x20, 0x7F):
    i = idx_of.get(cp)
    if i is None:
        report.append((chr(cp), None, 0))
        continue
    x, y = U[i], V[i]
    if not (0 <= x < AW and 0 <= y < AH):
        report.append((chr(cp), i, -1))
        continue
    if cp == 0x20:                       # 空格：只清空，不画
        y2, x2 = min(y + CELL, AH), min(x + CELL, AW)
        atlas[y:y2, x:x2] = 0
        report.append((' ', i, 0))
        continue
    g = render(chr(cp))
    y2, x2 = min(y + CELL, AH), min(x + CELL, AW)
    atlas[y:y2, x:x2] = 0                # 先清空
    h = min(BOX, y2 - y)
    w = min(BOX, x2 - x)
    atlas[y:y + h, x:x + w] = g[:h, :w]
    ink = int((g[:h, :w] > 24).sum())
    report.append((chr(cp), i, ink))
    painted += 1

print()
print('=== 重绘结果（前 40 项）===')
for ch, i, ink in report[:40]:
    print('  %-4r 索引 %-5s 墨量 %s' % (ch, i, ink))
empty = [ch for ch, i, ink in report if i is not None and ink == 0 and ch != ' ']
print()
print('重绘 %d 个字形；无墨迹的: %s' % (painted, ''.join(empty) if empty else '无'))

# ---------- 5. 打包 ----------
v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'g_peg_pc'), atlas.tobytes())
out = os.path.join(OUTDIR, 'patch.vpp_pc')
v2.save(out)
print()
print('写出 %s (%d 字节)' % (out, os.path.getsize(out)))

# ---------- 6. 复验：重新读出来再看一遍 ----------
chk = Vpp(out)
A2 = np.frombuffer(chk.read(chk.find('fnt_chinese', 'g_peg_pc')), np.uint8).reshape(AH, AW)
print('复验墨量（前 12 项）: %s'
      % [int((A2[V[idx_of[cp]]:V[idx_of[cp]] + BOX, U[idx_of[cp]]:U[idx_of[cp]] + BOX] > 24).sum())
         for cp in range(0x20, 0x2C) if cp in idx_of])
