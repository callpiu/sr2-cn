# -*- coding: utf-8 -*-
# STRUCTURE-SAFE probe: equal-length in-place glyph swap inside ALL static_CH blob
# copies (old in-place blob + v532 appended blob). No entry/size/offset changes.
#   弟兄们 -> 车耐久   (3 units, equal length)
#   免遭袭击 -> 一二三四 (4 units, equal length)
import sys, re, struct, hashlib
sys.path.insert(0, 'F:/sr2-cn')

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
data = bytearray(open(P, 'rb').read())
md5_before = hashlib.md5(data).hexdigest()
print('before md5:', md5_before, '(expect 641e5df5... = clean v532)')
assert md5_before == '641e5df5bf74383ffe47b795a9796210'

# charlist
import io
vpp_data = data
# extract charlist via sr2lib on a temp copy is heavy; instead parse vpp entries manually is complex.
# Use sr2lib read-only from the same bytes:
from sr2lib import Vpp
import tempfile, os, shutil
tmp = tempfile.mktemp(suffix='.vpp_pc')
open(tmp, 'wb').write(data)
vpp = Vpp(tmp)
cl = vpp.find('charlist_CH', 'txt')
clb = vpp.read(cl)
end = clb.find(b'//ENDOFFILE')
CPS = [int(x) for x in re.findall(rb'\d+', clb[:end if end > 0 else len(clb)])]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}

def enc(s):
    return b''.join(struct.pack('>H', CP2IDX[ord(c)] + 0x20) for c in s)

pat1 = enc('弟兄们')
rep1 = enc('车耐久')
pat2 = enc('免遭袭击')
rep2 = enc('一二三四')
assert len(pat1) == len(rep1) and len(pat2) == len(rep2)

def replace_all(buf, pat, rep):
    offs = []
    start = 0
    while True:
        k = buf.find(pat, start)
        if k < 0:
            break
        buf[k:k + len(pat)] = rep
        offs.append(k)
        start = k + len(rep)
    return offs

o1 = replace_all(data, pat1, rep1)
o2 = replace_all(data, pat2, rep2)
print('弟兄们->车耐久 patched %d sites:' % len(o1), [hex(x) for x in o1])
print('免遭袭击->一二三四 patched %d sites:' % len(o2), [hex(x) for x in o2])

open(P, 'wb').write(data)
print('after md5:', hashlib.md5(open(P, 'rb').read()).hexdigest())

# verify via entry-read (v532 blob) and absolute reads (old blob)
v2 = Vpp(P)
e = v2.find('static_CH', 'le_strings')
b2 = v2.read(e)
print('entry blob contains 车耐久:', enc('车耐久') in b2, ' contains 弟兄们:', pat1 in b2)
print('entry blob contains 一二三四:', enc('一二三四') in b2, ' contains 免遭袭击:', pat2 in b2)
f = open(P, 'rb')
f.seek(0x1C16B3E); print('old blob @0x1C16B3E:', f.read(6).hex(), '(expect 车耐久 slots)')
f.seek(0x2E1AF60); print('v532 blob @0x2E1AF60:', f.read(8).hex(), '(expect 一二三四 slots)')
f.close()
os.remove(tmp)
print('DONE')
