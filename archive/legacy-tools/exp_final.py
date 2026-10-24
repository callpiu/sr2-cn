import sys, struct, re, hashlib
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)
cl = vpp.find('charlist_CH', 'txt'); clb = vpp.read(cl)
end = clb.find(b'//ENDOFFILE'); body = clb[:end if end>0 else len(clb)]
CPS = [int(x) for x in re.findall(rb'\d+', body)]
CP2IDX = {cp:i for i,cp in enumerate(CPS)}

def slot_encode(s):
    out = []
    for ch in s:
        o = ord(ch)
        assert o in CP2IDX, 'char not in charlist: %s (U+%04X)' % (ch, o)
        out.append(CP2IDX[o] + 0x20)
    return out

ent = vpp.find('static_CH', 'le_strings')
blob = vpp.read(ent)
magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
assert magic == 0xA84C7F73
A0 = 12 + nb*8

recs = []
for i in range(count):
    off = struct.unpack_from('<I', blob, A0+i*4)[0]
    id1, id2 = struct.unpack_from('<HH', blob, off)
    j = off+4; units=[]
    while j+2 <= len(blob):
        u = struct.unpack_from('<H', blob, j)[0]
        if u == 0: break
        units.append(u); j += 2
    recs.append([id1, id2, units])

# distinctive test strings, NO format codes, all chars confirmed in charlist
new_text = {
    0x84F287ED: '面包车耐久测试文本',
    0x10AF1E62: '测试一二三四五六七八九',
}
for r in recs:
    h = (r[0]<<16)|r[1]
    if h in new_text:
        r[2] = slot_encode(new_text[h])
        print('REPLACE %08X -> %r' % (h, new_text[h]))

# rebuild blob (BE units)
rec_area_start = A0 + count*4
rec_bytes = bytearray(); offsets=[]
for (id1,id2,units) in recs:
    offsets.append(len(rec_bytes)+rec_area_start)
    rec_bytes += struct.pack('<HH', id1, id2)
    for u in units:
        rec_bytes += struct.pack('>H', u)   # BIG-ENDIAN units
    rec_bytes += struct.pack('>H', 0)
ptr_array = b''.join(struct.pack('<I', o) for o in offsets)
new_blob = blob[:12] + blob[12:A0] + ptr_array + bytes(rec_bytes)

before = hashlib.md5(open(P,'rb').read()).hexdigest()
vpp.replace_body_appended(ent, new_blob)
vpp.save(P)
after = hashlib.md5(open(P,'rb').read()).hexdigest()
print('md5 before=%s after=%s' % (before, after))

# VERIFY via correct API
v2 = Vpp(P); e2 = v2.find('static_CH','le_strings'); b2 = v2.read(e2)
m2,_,nb2,c2 = struct.unpack_from('<IHHI', b2, 0); A0b = 12+nb2*8
def dec(b2, off):
    j=off+4; u=[]; 
    while j+2<=len(b2):
        v=struct.unpack_from('<H',b2,j)[0]
        if v==0: break
        u.append(v); j+=2
    return ''.join(chr(CPS[v-0x20]) if 0<=v-0x20<len(CPS) else '?' for v in u)
ok=True
for i in range(c2):
    off=struct.unpack_from('<I',b2,A0b+i*4)[0]
    id1,id2=struct.unpack_from('<HH',b2,off)
    h=(id1<<16)|id2
    if h in new_text:
        d=dec(b2,off); good=(d==new_text[h]); ok=ok and good
        print('  VERIFY %08X => %r (%s)' % (h, d, 'OK' if good else 'MISMATCH'))
print('\nnb=%d count=%d  ALL DEPLOYED CORRECTLY:', nb2, c2, ok)
