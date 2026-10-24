import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

v = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
blob = v.read(v.find('static_US', 'le_strings'))

def U16(s):
    return b''.join(struct.pack('>H', ord(c)) for c in s)

for probe in ['Dont worry, Father', "Don't worry, Father", 'Father... I', 'Father, I will', 'Father I', 'Father,']:
    print(repr(probe), blob.count(U16(probe)))

print('--- US records containing ather ---')
i = 0
res = []
while i + 2 <= len(blob):
    j = i
    out = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 400:
            break
    if out:
        t = ''.join(chr(x) if 32 <= x < 0x7f else '' for x in out)
        if 'ather' in t:
            res.append((i, len(out), t))
        i = j + 2
    else:
        i += 2
print('total', len(res))
for off, n, t in res:
    print('%08X %d %s' % (off, n, t[:120]))