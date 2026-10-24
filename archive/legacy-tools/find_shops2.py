# -*- coding: utf-8 -*-
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

def show(title, pred, limit=40):
    print()
    print('=== %s ===' % title)
    n = 0
    for off, o in CH:
        if len(o) < 3: continue
        t = D(o[2:])
        core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ').strip()
        if pred(core):
            n += 1
            if n <= limit:
                print('  off=%08X ID=%08X %r' % (off, (o[0] << 16) | o[1], core[:70]))
    print('  total', n)

# 用户截图里的店名（含各种空格/引号变体）
for kw in ['Sunsinger', 'Somer', 'PHUC', 'PHUC MI', 'Encanto', 'Needle', "Rusty",
           "Rusty's", 'Rusty ']:
    show('kw=%r' % kw, lambda c, k=kw: k.lower() in c.lower(), limit=12)

# 圣徽 / 圣徒街
show('含圣徽', lambda c: '圣徽' in c)
show('含圣徒街', lambda c: '圣徒街' in c)
show('含萨默塞特', lambda c: '萨默塞特' in c)