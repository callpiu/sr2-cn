import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

# 英文表：按同样的桶结构扫，找出 "Waiting for Players" 的记录 ID
v = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
blob = v.read(v.find('static_US', 'le_strings'))

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

def A(sl):
    return ''.join(chr(x) if 32 <= x < 0x7f else '' for x in sl)

print('=== US: 界面 label 类短记录（Waiting / Leave Game / Single Player） ===')
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if t in ('Waiting for Players', 'Waiting for Player...', 'Leave Game', 'Single Player',
             'Waiting for other player...', 'Waiting for Host'):
        print('%08X  ID=%08X  slots=%d  %r' % (off, (o[0] << 16) | o[1], len(o), t))

print()
print('=== US: 含 COOP / LOBBY / HOST 的短记录 ===')
c = 0
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if len(t) < 45 and any(k in t.upper() for k in ['COOP', 'LOBBY', 'HOST', 'CO-OP']):
        c += 1
        if c <= 40:
            print('%08X  ID=%08X  %r' % (off, (o[0] << 16) | o[1], t))
print('total', c)