import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
P = G + 'patch.vpp_pc'
buf = open(P, 'rb').read()
v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def S(w):
    return struct.pack('>H', CL.index(ord(w)) + 0x20)

def dec(b):
    out = []
    for i in range(0, len(b) - 1, 2):
        x = struct.unpack_from('>H', b, i)[0]
        if x == 0:
            out.append('|')
        elif x < 0x20:
            out.append('^%02X' % x)
        elif x - 0x20 < len(CL):
            out.append(chr(CL[x - 0x20]))
        else:
            out.append('?')
    return ''.join(out)

targets = [0x0287C940, 0x02889496, 0x02E62988, 0x02E6D298]
print('=== 归属条目 ===')
ents = [(ds + e['body'], ds + e['body'] + e['size'], e['name'] + '.' + e['ext']) for e in v.entries()]
for t in targets:
    hit = [nm for s, en, nm in ents if s <= t < en]
    print('%08X -> %s' % (t, hit if hit else '(表外松散区)'))

print()
print('=== 三张 CH 表全扫 神父/父亲 ===')
for nm, ext in [('static_CH', 'le_strings'), ('voice_script_CH', 'le_strings'),
                ('platform_pc_CH', 'le_strings'), ('static_US', 'le_strings')]:
    blob = v.read(v.find(nm, ext))
    for kw in ['神父', '父亲']:
        pat = S(kw[0]) + S(kw[1])
        if nm == 'static_US':
            pat = kw.encode('utf-16-be')
        cnt = blob.count(pat)
        print('  %-18s %s = %d' % (nm, kw, cnt))

print()
print('=== 上下文：把 4 条记录前后各 30 slot 全dump ===')
for st in targets:
    en = st + 2
    while en + 2 <= len(buf) and buf[en:en + 2] != b'\x00\x00':
        en += 2
    back = st
    for _ in range(30):
        if back <= 2 or buf[back - 2:back] == b'\x00\x00':
            break
        back -= 2
    print('%08X  PREV: %s' % (st, dec(buf[back:st])))
    print('%08X  SELF: %s' % (st, dec(buf[st:en + 2])))