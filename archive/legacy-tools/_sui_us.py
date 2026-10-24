import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

# 在英文 static_US 表里找所有 SUI_ / LAN 相关记录
v = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
blob = v.read(v.find('static_US', 'le_strings'))
print('static_US size', len(blob))

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
print('US records', len(res))

def A(sl):
    return ''.join(chr(x) if 32 <= x < 0x7f else '' for x in sl)

print()
print('=== US records containing SUI_ or _LAN or COOP ===')
c = 0
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if 'SUI_' in t or 'LAN_' in t or 'COOP' in t:
        c += 1
        if c <= 50:
            print('%08X  %s' % (off, t[:110]))
print('total', c)

print()
print('=== US records withWaiting/players wording (对照中文"等待玩家……") ===')
c = 0
for off, o in res:
    t = A(o[2:] if len(o) > 2 else o)
    if t.strip().startswith('Waiting') and len(t) < 40:
        c += 1
        if c <= 40:
            print('%08X  %r' % (off, t))
print('total', c)