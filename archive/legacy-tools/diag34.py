# -*- coding: utf-8 -*-
# diag34: 用双字体坐标数组 + 交叉图集配对，预测乱码并对照用户转写
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
patch = Vpp(GAME + r'\patch.vpp_pc')
common = Vpp(GAME + r'\common.vpp_pc')

cl = patch.read(patch.find('charlist_CH', 'txt'))
CPS = [c for c in (int(x) for x in re.findall(rb'\d+', cl)) if 0 < c < 0x20000]
CHR = ''.join(chr(c) for c in CPS)

def fontbuf(vp):
    for e in vp.entries():
        if 'fnt_chinese' in e['name'] and 'vf3' in e['ext']:
            return vp.read(e)

pb, cb = fontbuf(patch), fontbuf(common)
Np, Nc = 2795, 2838

def pos_arr(buf, off, n):
    return list(struct.unpack_from(f'<{2*n}H', buf, off))  # [(x,y),...] flattened

# patch: arrays at 0xAF6C and 0xDB18 (= 0xAF6C + 4*N)
pP1 = pos_arr(pb, 0xAF6C, Np)
pP2 = pos_arr(pb, 0xAF6C + 4 * Np, Np)
# common: array region = file end - 2*4*N (mirror patch layout)
cOff = len(cb) - 8 * Nc
cP1 = pos_arr(cb, cOff, Nc)
cP2 = pos_arr(cb, cOff + 4 * Nc, Nc)
print('common candidate offset:', hex(cOff))
print('patch POS1[:8] :', list(zip(pP1[::2], pP1[1::2]))[:8])
print('patch POS2[:8] :', list(zip(pP2[::2], pP2[1::2]))[:8])
print('common POS1[:8]:', list(zip(cP1[::2], cP1[1::2]))[:8])
print('common POS2[:8]:', list(zip(cP2[::2], cP2[1::2]))[:8])

def cells(flat):
    return list(zip(flat[::2], flat[1::2]))

p1c, p2c, c1c, c2c = cells(pP1), cells(pP2), cells(cP1), cells(cP2)

def inv(cs, name):
    m = {}
    dup = 0
    for i, c in enumerate(cs):
        if c in m: dup += 1
        else: m[c] = i
    print(f'{name}: unique={len(m)}/{len(cs)} dup={dup} sentinel_count={cs.count((65535,65535))+(65535,)==() if False else sum(1 for x in cs if 65535 in x)}')
    return m

invP1 = inv(p1c, 'patch POS1')
invP2 = inv(p2c, 'patch POS2')
invC1 = inv(c1c, 'common POS1')
invC2 = inv(c2c, 'common POS2')

# where do patch/common POS1 diverge?
div = None
for i in range(min(Np, Nc)):
    if p1c[i] != c1c[i]:
        div = i
        break
print('first divergence POS1 patch vs common at glyph', div)
if div is not None:
    print('  patch around:', p1c[div-2:div+4])
    print('  common around:', c1c[div-2:div+4])

# ---- garble prediction under cross combos ----
# slot -> g = slot-0x20 ; screen glyph = inv[combo font POS[g]] rendered on other atlas
REC1_slots = [0x193,0x74c,0x9b4,0x84d,0x12c,0xa8b,0x918,0x193,0x74c,0x1a7,0x4c6]
TRUE1 = '你的弟兄们需要你的保护'
GARB1 = '任璨偶巧位雄衡任璨伪该'
REC2_slots = [0x193,0x74c,0x9b4,0x84d,0x12c,0x918,0x1fe,0x265,0x955,0x1f6,0x7cb,0x720,0x487,0xb06,0x1a7,0x4c6,0x164,0x16c,0x10a,0x145,0x10f,0x2fb]
TRUE2 = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'
GARB2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'

def predict(posFont, invAtlas, slots):
    out = []
    for s in slots:
        g = s - 0x20
        cell = posFont[g]
        gg = invAtlas.get(cell)
        out.append(CHR[gg] if gg is not None and gg < len(CHR) else '?')
    return ''.join(out)

combos = [
    ('commonPOS -> atlasA', c1c, invP1),
    ('patchPOS  -> atlasB', p1c, invC1),
    ('commonPOS2-> atlasA', c2c, invP2),
    ('patchPOS2 -> atlasB', p2c, invC2),
    ('control: patchPOS->atlasA (correct)', p1c, invP1),
]
for name, pf, ia in combos:
    r1 = predict(pf, ia, REC1_slots)
    r2 = predict(pf, ia, REC2_slots)
    print(f'\n--- {name} ---')
    print('REC1 predict:', r1)
    print('REC1 actual :', GARB1, ' match=', r1 == GARB1)
    print('REC2 predict:', r2)
    print('REC2 actual :', GARB2, ' match=', r2 == GARB2)
