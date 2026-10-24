import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
blob = v.read(v.find('static_CH', 'le_strings'))

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def dec(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

# 顺序扫出全部记录
res = []
i = 0
while i + 2 <= len(blob):
    j = i
    out = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 600:
            break
    if out:
        res.append((i, out))
        i = j + 2
    else:
        i += 2
print('records', len(res))
idx = dict((o, k) for k, (o, _) in enumerate(res))

for tgt in [0x000355F0, 0x000357E6]:
    if tgt in idx:
        k = idx[tgt]
        print()
        print('=== %08X ===' % tgt)
        for o2, s2 in res[max(0, k - 6):k + 7]:
            mark = '  <<<' if o2 == tgt else ''
            print('%08X  %s%s' % (o2, dec(s2[2:] if len(s2) > 2 else s2)[:100], mark))

# 搜 SUI_ 风格的下划线大写 tag 记录（ASCII 全大写+下划线）
print()
print('=== 疑似 tag 记录（含多个 _ 且全大写） ===')
cnt = 0
for o2, s2 in res:
    t = dec(s2[2:] if len(s2) > 2 else s2)
    if t.count('_') >= 3 and t.replace('_', '').replace(' ', '').isupper() and t.isascii():
        cnt += 1
        if cnt <= 60:
            print('%08X  %s' % (o2, t[:100]))
print('total tag-like:', cnt)