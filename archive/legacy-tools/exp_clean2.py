import sys, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)
cl = vpp.find('charlist_CH', 'txt'); clb = vpp.read(cl)
end = clb.find(b'//ENDOFFILE'); body = clb[:end if end>0 else len(clb)]
CPS = [int(x) for x in re.findall(rb'\d+', body)]
CP2IDX = {cp:i for i,cp in enumerate(CPS)}

ent = vpp.find('static_CH', 'le_strings')
blob = vpp.read(ent)
magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
A0 = 12 + nb*8

def decode(units, order):
    out=[]
    for u in units:
        idx = (u if order=='raw' else struct.unpack(order, struct.pack('<H',u))[0]) - 0x20
        # u is already a u16; for BE storage, the value itself IS big-endian-represented;
        # but we read raw u16 from file. If stored BE, the raw u16 value we read with '<H' is wrong.
        # So: re-extract using proper order from the 2 bytes.
        out.append(idx)
    return out

# find REC1 and dump raw bytes + both interpretations
for i in range(count):
    off = struct.unpack_from('<I', blob, A0+i*4)[0]
    id1,id2 = struct.unpack_from('<HH', blob, off)
    h=(id1<<16)|id2
    if h in (0x84F287ED, 0x10AF1E62):
        j=off+4; raw=[]
        while j+2<=len(blob):
            u=struct.unpack_from('<H',blob,j)[0]
            if u==0: break
            raw.append(u); j+=2
        # interpret LE vs BE: take bytes and repack
        bs = b''.join(struct.pack('<H',u) for u in raw)
        le_vals = list(struct.unpack('<'+'H'*len(raw), bs))
        be_vals = list(struct.unpack('>'+'H'*len(raw), bs))
        def tostr(vals):
            return ''.join(chr(CPS[v-0x20]) if 0<=v-0x20<len(CPS) else '?' for v in vals)
        print('%08X LE-decode=%r' % (h, tostr(le_vals)))
        print('%08X BE-decode=%r' % (h, tostr(be_vals)))
