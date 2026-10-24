import sys, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)

# find static_CH entry
ent = None
for e in vpp.entries():
    if e['name'] == 'static_CH' and e['ext'] == 'le_strings':
        ent = e
        break
print('ENTRY static_CH:', ent)
body_off = ent['body']
body_size = ent['size']
print('  body_off=%d (0x%X)  size=%d (0x%X)' % (body_off, body_off, body_size, body_size))

buf = open(P, 'rb').read()
blob = buf[body_off:body_off+body_size]
print('  blob magic=%r nb=%d count=%d' % (blob[:4], struct.unpack_from('<H', blob, 6)[0], struct.unpack_from('<I', blob, 8)[0]))

# parse records of this live blob
def parse_records(b):
    magic, ver, nb, count = struct.unpack_from('<IHHI', b, 0)
    A0 = 12 + nb*8
    recs = []
    for i in range(count):
        off = struct.unpack_from('<I', b, A0 + i*4)[0]
        if off == 0 or off >= len(b):
            recs.append((off, None)); continue
        id1, id2 = struct.unpack_from('<HH', b, off)
        # text starts at off+4, UTF-16BE units until 0x0000
        j = off+4; units=[]
        while j+2 <= len(b):
            u = struct.unpack_from('<H', b, j)[0]
            if u == 0: break
            units.append(u); j += 2
        recs.append((off, (id1,id2,units)))
    return recs

recs = parse_records(blob)
# find target hash
targets = {0x84F287ED:'REC1 homies need protection', 0x10AF1E62:'REC2 heading out deals'}
found = {}
for off,(id1,id2,units) in recs:
    h = (id1<<16)|id2
    if h in targets:
        found[h] = (off, units)
        print('  LIVE blob has %08X (%s) at off=%d units=%d first=%r' % (h, targets[h], off, len(units), units[:6]))

if not found:
    print('  !! target hashes NOT in live entry-pointed blob')

# Also: where in the WHOLE file do these byte patterns live?
print('\n=== whole-file pattern scan ===')
def slot_bytes(s):
    # slot-encode a string using charlist_CH
    cl = vpp.find('charlist_CH','txt'); clb = vpp.read(cl)
    end = clb.find(b'//ENDOFFILE'); body = clb[:end if end>0 else len(clb)]
    CPS = [int(x) for x in re.findall(rb'\d+', body)]
    CP2IDX = {cp:i for i,cp in enumerate(CPS)}
    out = b''
    for ch in s:
        idx = CP2IDX[ord(ch)]
        out += struct.pack('<H', idx+0x20)
    return out

test1 = slot_bytes('面包车耐久测试文本')
test2 = slot_bytes('你的弟兄们需要你的保护')
orig1 = slot_bytes('你的弟兄们需要你的保护')  # same as test2 actually
# search
for name, pat in [('TEST1 面包车耐久测试文本', test1), ('TEST2 你的弟兄们需要你的保护', test2)]:
    idxs = []
    start=0
    while True:
        i = buf.find(pat, start)
        if i<0: break
        idxs.append(i); start=i+2
    print('  %s -> %d hit(s) at %s' % (name, len(idxs), [hex(x) for x in idxs[:10]]))

# search the GARBLED screen text slot-encoded? No, garble is what screen shows; 
# but the ORIGINAL correct chinese of REC1 = 你的弟兄们需要你的保护 (without format). 
# The garble source data is the SLOT-encoded correct chinese. Let's see if that slot pattern exists:
orig_rec1 = slot_bytes('你的弟兄们需要你的保护')
idxs = []
start=0
while True:
    i = buf.find(orig_rec1, start)
    if i<0: break
    idxs.append(i); start=i+2
print('  ORIGINAL-correct (你的弟兄们需要你的保护) slot pattern -> %d hit(s) at %s' % (len(idxs), [hex(x) for x in idxs[:10]]))

# And search the FULL original REC1 with format codes (your弟兄们...need保护)
rec1_full = slot_bytes('你的') + b'[format][color:green]' + slot_bytes('弟兄们') + b'[/format]' + slot_bytes('需要你的保护')
# note: ASCII format chars are NOT slot-encoded, stored as raw ASCII. Let's build properly:
def mixed_slot(s):
    cl = vpp.find('charlist_CH','txt'); clb = vpp.read(cl)
    end = clb.find(b'//ENDOFFILE'); body = clb[:end if end>0 else len(clb)]
    CPS = [int(x) for x in re.findall(rb'\d+', body)]
    CP2IDX = {cp:i for i,cp in enumerate(CPS)}
    out=b''
    for ch in s:
        o=ord(ch)
        if o<0x80:
            out+=bytes([o])  # ASCII raw (but format codes are ASCII)
        else:
            out+=struct.pack('<H', CP2IDX[o]+0x20)
    return out
rec1_mixed = mixed_slot('你的[format][color:green]弟兄们[/format]需要你的保护')
idxs=[]
start=0
while True:
    i=buf.find(rec1_mixed,start)
    if i<0: break
    idxs.append(i); start=i+2
print('  ORIGINAL-with-format REC1 slot pattern -> %d hit(s) at %s' % (len(idxs), [hex(x) for x in idxs[:10]]))
