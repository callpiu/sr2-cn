import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

v = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
names = {}
for e in v.entries():
    names[e['name'] + '.' + e['ext']] = e
print('--- US-ish le_strings entries ---')
for k, e in sorted(names.items()):
    if 'le_strings' in k:
        print('  %-40s size=%d' % (k, e['size']))

blob = v.read(v.find('voice_script_US', 'le_strings'))
print()
print('voice_script_US size', len(blob))

def U16(s):
    return b''.join(struct.pack('>H', ord(c)) for c in s)

for probe in ['Father', 'Priest', 'Dad', 'Pop']:
    print('%s -> %d' % (probe, blob.count(U16(probe))))

print()
print('--- US voice records containing Father/Priest ---')
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
        if len(out) > 400:
            break
    if out:
        t = ''.join(chr(x) if 32 <= x < 0x7f else '' for x in out)
        if 'Father' in t or 'Priest' in t:
            print('%08X %d %s' % (i, len(out), t[:130]))
        i = j + 2
    else:
        i += 2