import sys, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)
print('data_start =', vpp.data_start)

# charlist codepoints (robust parse: newline-separated, ignore //ENDOFFILE)
cl = vpp.find('charlist_CH', 'txt')
clb = vpp.read(cl)
end = clb.find(b'//ENDOFFILE')
body = clb[:end if end > 0 else len(clb)]
CPS = [int(x) for x in re.findall(rb'\d+', body)]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}
print('charlist_CH entries:', len(CPS))

def slot_encode(s):
    out = []
    for ch in s:
        out.append(CP2IDX[ord(ch)] + 0x20)
    return out

def slot_decode(units):
    return ''.join(chr(CPS[u - 0x20]) if 0x20 <= u - 0x20 < len(CPS) else '?' for u in units)

# --- parse live static_CH blob via correct API ---
ent = vpp.find('static_CH', 'le_strings')
blob = vpp.read(ent)   # absolute blob bytes (read adds data_start)
print('\nstatic_CH blob len=%d magic=%r' % (len(blob), blob[:4]))
magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
print('ver=%d nb=%d count=%d' % (ver, nb, count))
A0 = 12 + nb * 8

# decode all records, find homies
recs = []
targets = {0x84F287ED: 'REC1 need protection', 0x10AF1E62: 'REC2 heading out deals'}
hits = {}
for i in range(count):
    off = struct.unpack_from('<I', blob, A0 + i*4)[0]
    id1, id2 = struct.unpack_from('<HH', blob, off)
    j = off + 4; units = []
    while j + 2 <= len(blob):
        u = struct.unpack_from('<H', blob, j)[0]
        if u == 0: break
        units.append(u); j += 2
    h = (id1 << 16) | id2
    recs.append((id1, id2, units))
    if h in targets:
        hits[h] = (off, units)
        print('  HIT %08X (%s): decode=%r' % (h, targets[h], slot_decode(units)))

# --- replace target texts with distinctive test strings (no format codes) ---
new_text = {
    0x84F287ED: '测试甲乙丙丁戊己庚',   # 9 chars, distinctive
    0x10AF1E62: '测试子丑寅卯辰巳午',   # 9 chars, distinctive
}
for i, (id1, id2, units) in enumerate(recs):
    h = (id1 << 16) | id2
    if h in new_text:
        recs[i] = (id1, id2, slot_encode(new_text[h]))
        print('  REPLACE %08X -> %r' % (h, new_text[h]))

# --- rebuild blob ---
rec_area_start = A0 + count * 4
rec_bytes = bytearray()
offsets = []
for (id1, id2, units) in recs:
    offsets.append(len(rec_bytes) + rec_area_start)
    rec_bytes += struct.pack('<HH', id1, id2)
    for u in units:
        rec_bytes += struct.pack('<H', u)
    rec_bytes += struct.pack('<H', 0)
ptr_array = b''.join(struct.pack('<I', o) for o in offsets)
header12 = blob[:12]
bucket_table = blob[12:A0]
new_blob = header12 + bucket_table + ptr_array + bytes(rec_bytes)
print('\nnew blob len=%d (was %d)' % (len(new_blob), len(blob)))

# --- deploy via correct API ---
vpp.replace_body_appended(ent, new_blob)
vpp.save(P)
print('saved.')

# --- VERIFY via read(ent) (correct API) ---
v2 = Vpp(P)
e2 = v2.find('static_CH', 'le_strings')
b2 = v2.read(e2)
m2, v2n, nb2, c2 = struct.unpack_from('<IHHI', b2, 0)
A0b = 12 + nb2*8
print('\nVERIFY: live static_CH blob len=%d nb=%d count=%d' % (len(b2), nb2, c2))
ok = True
for i in range(c2):
    off = struct.unpack_from('<I', b2, A0b + i*4)[0]
    id1, id2 = struct.unpack_from('<HH', b2, off)
    j = off+4; units=[]
    while j+2 <= len(b2):
        u = struct.unpack_from('<H', b2, j)[0]
        if u==0: break
        units.append(u); j+=2
    h=(id1<<16)|id2
    if h in new_text:
        dec = slot_decode(units)
        good = (dec == new_text[h])
        ok = ok and good
        print('  %08X => %r  (%s)' % (h, dec, 'OK' if good else 'MISMATCH'))
print('\nALL TARGETS CORRECTLY DEPLOYED:', ok)
