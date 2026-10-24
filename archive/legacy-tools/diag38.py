# -*- coding: utf-8 -*-
# diag38: 全盘搜索"乱码字面"的 slot 字节（任璨偶巧位雄衡任璨伪该 / REC2）
import sys, re, struct, glob, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = Vpp(GAME + r'\patch.vpp_pc')
CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
IDX = {c: i for i, c in enumerate(CPS)}

def slots_of(s):
    out = []
    for ch in s:
        r = IDX.get(ord(ch))
        if r is None:
            return None
        out.append(r + 0x20)
    return out

def patterns(s):
    slots = slots_of(s)
    if slots is None:
        return []
    be = b''.join(struct.pack('>H', v) for v in slots)
    le = b''.join(struct.pack('<H', v) for v in slots)
    return [('slotBE', be), ('slotLE', le)]

G1 = '任璨偶巧位雄衡任璨伪该'
G2 = '任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮'
# REC2 乱码里逗号显示为空格，也准备不带"携伪"接缝的两个半段以防万一
G2a = '任璨偶巧位校衡勾远藐乱携'
G2b = '伪该亡位通像匪冰挺拮'

targets = {}
for name, s in [('G1', G1), ('G2', G2), ('G2a', G2a), ('G2b', G2b)]:
    for tag, pat in patterns(s):
        targets[f'{name}/{tag}'] = pat
        print(f'{name}/{tag}: {pat.hex()}  ({len(pat)} bytes)')

# scan every file in game dir (all sizes)
files = [f for f in glob.glob(GAME + r'\**\*', recursive=True) if os.path.isfile(f)]
print('\nscanning', len(files), 'files...')
for f in files:
    try:
        sz = os.path.getsize(f)
        if sz == 0:
            continue
        d = open(f, 'rb').read()
    except Exception:
        continue
    hits = []
    for k, pat in targets.items():
        i = d.find(pat)
        while i >= 0:
            hits.append((k, i))
            i = d.find(pat, i + 1)
    if hits:
        print(os.path.basename(f), sz, hits)
