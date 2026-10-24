# -*- coding: utf-8 -*-
# diag33: 双字体位置数组数值验证
# 假设：字幕 UI 绑定 common 的 fnt_chinese(N=2838)，图集却是 patch 的 atlas A
#       → 同一 glyph idx 解析到不同图集 cell → 确定性乱码
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
patch = Vpp(GAME + r'\patch.vpp_pc')
common = Vpp(GAME + r'\common.vpp_pc')

# ---- charlist ----
cl = patch.read(patch.find('charlist_CH', 'txt'))
CPS = [int(x) for x in re.findall(rb'\d+', cl)]
CPS = [c for c in CPS if 0 < c < 0x20000]
IDX = {cp: i for i, cp in enumerate(CPS)}
print('charlist_CH:', len(CPS))

# ---- fonts ----
def getfont(vp, tag):
    for e in vp.entries():
        if 'fnt_chinese' in e['name'] and 'vf3' in e['ext']:
            b = vp.read(e)
            print(f'{tag}: entry {e["name"]}.{e["ext"]} size={len(b)}')
            return b
    print(tag, 'NOT FOUND')
    return None

pb = getfont(patch, 'patch font')
cb = getfont(common, 'common font')

def parse_records(buf):
    # reuse sr2lib.parse_vfnt for header/records
    from sr2lib import parse_vfnt
    header, recs, tail = parse_vfnt(buf)
    return header, recs, tail

ph, pr, _ = parse_records(pb)
ch_, cr, _ = parse_records(cb)
print('patch header:', ph)
print('common header:', ch_)
Np, Nc = len(pr), len(cr)
print('N patch =', Np, ' N common =', Nc)

# ---- extract u16 arrays at candidate offsets ----
def u16arr(buf, off, n):
    return list(struct.unpack_from(f'>{n}H', buf, off))

# known hint: U@0xAF6C, V@0xDB18 (N items each). For patch N=2795: 2N=5590
for tag, buf, N in (('patch', pb, Np), ('common', cb, Nc)):
    print(f'--- {tag} N={N} ---')
    # try documented offsets and scan for plausible arrays
    for off in (0xAF6C,):
        if off + 4 * N <= len(buf):
            U = u16arr(buf, off, N)
            V = u16arr(buf, off + 2 * N, N)
            print(f'U@{off:#x}: first10={U[:10]} max={max(U)} mono={all(U[i]<=U[i+1] for i in range(N-1))}')
            print(f'V@{off+2*N:#x}: first10={V[:10]} max={max(V)} mono={all(V[i]<=V[i+1] for i in range(N-1))}')

# ---- dump REC slots from live static_CH (BE) ----
ent = patch.find('static_CH', 'le_strings')
blob = patch.read(ent)
def find_rec(h):
    id1, id2 = h >> 16, h & 0xFFFF
    pat = struct.pack('<HH', id1, id2)
    out = []
    i = blob.find(pat)
    while i >= 0:
        # record: ids at off, text at off+4, terminated 0x0000
        out.append(i)
        i = blob.find(pat, i + 1)
    return out

def units(h):
    id1, id2 = h >> 16, h & 0xFFFF
    pat = struct.pack('<HH', id1, id2)
    i = blob.find(pat)
    if i < 0:
        return None
    off = i + 4
    us = []
    while off + 2 <= len(blob):
        v = struct.unpack_from('>H', blob, off)[0]
        off += 2
        if v == 0:
            break
        us.append(v)
    return us

REC1 = 0x84F287ED
REC2 = 0x10AF1E62
u1 = units(REC1)
u2 = units(REC2)
print('REC1 units:', [hex(v) for v in u1])
print('REC2 units:', [hex(v) for v in u2])

# content chars = units >= 0x100 (format tags are ASCII-range units)
cjk1 = [v for v in u1 if v >= 0x100]
cjk2 = [v for v in u2 if v >= 0x100]
print('REC1 content slots:', [hex(v) for v in cjk1], 'n=', len(cjk1))
print('REC2 content slots:', [hex(v) for v in cjk2], 'n=', len(cjk2))

# user-transcribed screen garble (authoritative)
g1 = '任璨偶巧位雄衡任璨伪该'          # 你的弟兄们需要你的保护
g2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'
t2 = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'

def pairs(cjk_slots, garble, true_str):
    tc = [c for c in true_str]
    n = min(len(cjk_slots), len(garble), len(tc))
    res = []
    for i in range(n):
        g = cjk_slots[i] - 0x20          # glyph idx
        sc = garble[i]
        r = IDX.get(ord(sc))
        res.append((tc[i], cjk_slots[i], g, sc, r))
    return res

P1 = pairs(cjk1, g1, '你的弟兄们需要你的保护')
print('\n=== REC1 mapping (true, slot, glyphidx, screen, screen_rank) ===')
for p in P1:
    print(p)
