# -*- coding: utf-8 -*-
"""扫描 vf3 全表，找到渲染为指定目标字的 vf3 索引。
用模板匹配：把已知字的渲染图作为模板，在全表中找最相似的。
更简单：直接渲染一批索引，人眼比对。但此处自动化：用 ascii 像素模板匹配太慢。
改为：利用已知 charlist 字 -> 该字的标准渲染模板 -> 在全表 2795 个 cell 中找最佳匹配。
模板来源：我们并不知道"正确"的字长啥样。所以换思路：
- 取 charlist 中某字（如 '你'）在 vf3 中按 index 渲染 = 使（已证）。
- 说明存在某种置换 P: vf3[P(i)] = charlist[i]。
- 若 P 是常量偏移，则对所有 i 成立。测偏移。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
cn = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]
vb = v.read(v.find('fnt_chinese', 'vf3_pc'))
N = struct.unpack('<I', vb[8:12])[0]
urec = 0xD0 + N * 16
U = struct.unpack('<%di' % N, vb[urec:urec + N * 4])
Vb = urec + N * 4
V = struct.unpack('<%di' % (N - 5), vb[Vb:Vb + (N - 5) * 4])
pe = v.read(v.find('fnt_chinese', 'g_peg_pc'))
rgb, alpha = dxt3_decode(pe, 2048, 2048)
rgb = np.asarray(rgb); alpha = np.asarray(alpha)
H, W = rgb.shape[0], rgb.shape[1]

def get_cell(k, cell=32):
    x = U[k]; y = V[k] if k < len(V) else 0
    return alpha[y:y+cell, x:x+cell]

# 用像素指纹法：把每个 cell 降采样成 8x8 灰度，构建哈希；找重复/匹配
def fp(k):
    a = get_cell(k)
    im = Image.fromarray(a.astype('uint8'), 'L').resize((10, 10), Image.BILINEAR)
    return np.asarray(im).astype(np.int16)

# 目标：找 charlist[371]='你' 的真实 vf3 索引。
# 我们无法直接知道"你"长啥样 —— 但可以用同一渲染器的已知正确样本。
# 已知：游戏内正确显示的字符来自哪里？—— 由 vf3 渲染。
# 所以"你"的正确 vf3 索引，就是某个 k 使 vf3[k] 图形 == 你。
# 而"你"的图形我们可从「已正确显示的其它 CH 文本」或「原厂繁体 vf3」获得。
# 先做一个更直接的实验：比较 patch.vpp 的 vf3 与 pristine patch.vpp 的 vf3 是否相同。
print('patch vf3 sha', __import__('hashlib').sha1(vb).hexdigest())
pv = Vpp('F:/sr2-cn/pristine/patch.vpp_pc')
pvb = pv.read(pv.find('fnt_chinese', 'vf3_pc'))
print('pristine vf3 size', len(pvb), 'sha', __import__('hashlib').sha1(pvb).hexdigest())
pN = struct.unpack('<I', pvb[8:12])[0]
print('pristine N', pN)
pU = struct.unpack('<%di'%pN, pvb[0xD0+pN*16:0xD0+pN*16+pN*4])
print('pristine U[0:5]', pU[:5])
print('patch U[0:5]', U[:5])
print('U 序列相同?', pU[:50] == U[:50])
