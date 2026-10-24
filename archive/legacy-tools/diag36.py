# -*- coding: utf-8 -*-
# diag36: 寻找"另一份字表"——字幕 UI 实际使用的 glyph 顺序
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
CPS = [int(l) for l in Vpp(GAME + r'\patch.vpp_pc').read(
    Vpp(GAME + r'\patch.vpp_pc').find('charlist_CH', 'txt'))
    .decode('utf-8').split('\n') if l.strip().isdigit()]

# 9 constraints: glyph_idx -> screen char
CONS = [(371, '任'), (1836, '璨'), (2452, '偶'), (2093, '巧'), (268, '位'),
        (2667, '雄'), (2296, '衡'), (391, '伪'), (1190, '该')]

def check(name, L):
    if L is None or len(L) <= max(g for g, _ in CONS):
        print(f'{name}: too short ({len(L) if L else 0})')
        return
    ok = sum(1 for g, c in CONS if L[g] == c)
    print(f'{name}: {ok}/{len(CONS)}', ''.join(L[g] for g, _ in CONS))

# ---- candidate 1: sorted variants of CPS ----
import unicodedata
def gbkkey(cp):
    try: return chr(cp).encode('gbk')
    except Exception: return b'\xff\xff\xff'
def big5key(cp):
    try: return chr(cp).encode('big5')
    except Exception: return b'\xff\xff\xff'

L_sorted = sorted(CPS)
check('CPS sorted by codepoint', [chr(c) for c in L_sorted])
check('CPS sorted by GBK bytes', [chr(c) for c in sorted(CPS, key=gbkkey)])
check('CPS sorted by BIG5 bytes', [chr(c) for c in sorted(CPS, key=big5key)])
check('CPS sorted by UTF16BE bytes', [chr(c) for c in sorted(CPS, key=lambda c: struct.pack('>H', c))])
check('CPS sorted by UTF16LE bytes', [chr(c) for c in sorted(CPS, key=lambda c: struct.pack('<H', c))])

# ---- candidate 2: charlist files in ALL containers ----
import glob, os
print('\n=== charlist entries in all vpp containers ===')
for vppf in glob.glob(GAME + r'\*.vpp_pc'):
    try:
        vp = Vpp(vppf)
        for e in vp.entries():
            n = (e['name'] + '.' + e['ext']).lower()
            if 'charlist' in n or (e['ext'].lower() == 'txt' and 'list' in n):
                b = vp.read(e)
                lines = [l for l in b.decode('utf-8', 'replace').split('\n') if l.strip().isdigit()]
                print(f'{os.path.basename(vppf)}: {e["name"]}.{e["ext"]} size={len(b)} numeric_lines={len(lines)}')
                if lines:
                    L = [chr(int(x)) for x in lines]
                    check('  -> ' + e['name'], L)
    except Exception as ex:
        print(vppf, 'ERR', ex)

# ---- candidate 3: loose charlist files ----
print('\n=== loose charlist files ===')
for pat in (GAME + r'\**\*charlist*', GAME + r'\**\*.txt'):
    for f in glob.glob(pat, recursive=True):
        print(' ', f, os.path.getsize(f))
