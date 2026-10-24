# -*- coding: utf-8 -*-
# diag35: 正确解析 U/V(i32) 双字体坐标，交叉配对预测乱码
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
patch = Vpp(GAME + r'\patch.vpp_pc')
common = Vpp(GAME + r'\common.vpp_pc')

CPS = [int(l) for l in patch.read(patch.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
CHR = ''.join(chr(c) for c in CPS)
Np, Nc = len(CPS), 2838

def fontbuf(vp):
    for e in vp.entries():
        if 'fnt_chinese' in e['name'] and 'vf3' in e['ext']:
            return vp.read(e)

pb, cb = fontbuf(patch), fontbuf(common)

def uv(buf, n, base=None):
    if base is None:
        base = len(buf) - 8 * n
    U = list(struct.unpack_from(f'<{n}i', buf, base))
    V = list(struct.unpack_from(f'<{n}i', buf, base + 4 * n))
    return U, V

pU, pV = uv(pb, Np, 0xAF6C)
cU, cV = uv(cb, Nc)
print('patch U[:6]', pU[:6], 'V[:6]', pV[:6])
print('common U[:6]', cU[:6], 'V[:6]', cV[:6])
puv = list(zip(pU, pV))
cuv = list(zip(cU, cV))
print('patch unique cells:', len(set(puv)), '/', Np)
print('common unique cells:', len(set(cuv)), '/', Nc)

# divergence
div = next((i for i in range(min(Np, Nc)) if puv[i] != cuv[i]), None)
print('first divergence at glyph', div)
if div is not None:
    print(' patch :', puv[max(0,div-2):div+3])
    print(' common:', cuv[max(0,div-2):div+3])

invP = {}
for i, c in enumerate(puv):
    invP.setdefault(c, i)
invC = {}
for i, c in enumerate(cuv):
    invC.setdefault(c, i)

REC1_slots = [0x193,0x74c,0x9b4,0x84d,0x12c,0xa8b,0x918,0x193,0x74c,0x1a7,0x4c6]
TRUE1 = '你的弟兄们需要你的保护'
GARB1 = '任璨偶巧位雄衡任璨伪该'
REC2_slots = [0x193,0x74c,0x9b4,0x84d,0x12c,0x918,0x1fe,0x265,0x955,0x1f6,0x7cb,0x720,0x487,0xb06,0x1a7,0x4c6,0x164,0x16c,0x10a,0x145,0x10f,0x2fb]
TRUE2 = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'
GARB2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'

def predict(uvFont, invAtlas, slots):
    out = []
    for s in slots:
        g = s - 0x20
        gg = invAtlas.get(uvFont[g], -1)
        out.append(CHR[gg] if 0 <= gg < len(CHR) else '?')
    return ''.join(out)

combos = [
    ('subtitle=commonUV@atlasA', cuv, invP),
    ('subtitle=patchUV@atlasB', puv, invC),
    ('control patchUV@atlasA(correct)', puv, invP),
    ('control commonUV@atlasB(correct)', cuv, invC),
]
for name, f, ia in combos:
    r1 = predict(f, ia, REC1_slots)
    r2 = predict(f, ia, REC2_slots)
    print(f'\n--- {name} ---')
    print('R1:', r1, 'match=', r1 == GARB1)
    print('R2:', r2, 'match=', r2 == GARB2)
