"""diag22: compare static_CH entry body-offset across patch backups + current.
If the offset is FIXED across versions -> mod overwrites in-place (game reads a
fixed location); my APPEND created a new block the game ignores. If it grows ->
append is the method. Also decode 0x84F287ED in each to see actual content."""
import sys, struct, os
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
FILES = [
    ('current(exp)', os.path.join(GAME, 'patch.vpp_pc')),
    ('v532_before_exp', os.path.join(GAME, 'patch.vpp_pc.v532_before_exp.bak')),
    ('v531_before_mirror', os.path.join(GAME, 'patch.vpp_pc.v531_before_mirror.bak')),
    ('v405bak', os.path.join(GAME, 'patch.vpp_pc.v405bak')),
    ('v522bak', os.path.join(GAME, 'patch.vpp_pc.v522bak')),
]

for label, path in FILES:
    if not os.path.exists(path):
        print('%-20s MISSING' % label); continue
    try:
        vp = Vpp(path)
    except Exception as ex:
        print('%-20s LOAD FAIL %s' % (label, ex)); continue
    e = vp.find('static_CH', 'le_strings')
    if e is None:
        print('%-20s no static_CH entry' % label); continue
    body_off = vp.data_start + e['body']
    blob = vp.read(e)
    # decode 0x84F287ED
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    A0 = 12 + nb*8
    txt = None
    for k in range(count):
        off = struct.unpack_from('<I', blob, A0+k*4)[0]
        id1, id2 = struct.unpack_from('<HH', blob, off)
        if (id1<<16)|id2 == 0x84F287ED:
            o = off+4; units=[]
            while True:
                u = struct.unpack_from('>H', blob, o)[0]; o+=2
                if u==0: break
                units.append(u)
            # charlist from THIS file
            cl = vp.find('charlist_CH','txt')
            CPS = [int(x) for x in vp.read(cl).decode('ascii','replace').split('//ENDOFFILE')[0].split() if x.isdigit()]
            s=[]
            for u in units:
                if u<0x80: s.append(chr(u))
                else:
                    i=u-0x20; s.append(chr(CPS[i]) if 0<=i<len(CPS) else '?')
            txt=''.join(s); break
    print('%-20s filesize=%-10d static_CH body_off=%-10d size=%-8d nb=%-5d  0x84F287ED=%r'
          % (label, len(vp.data), body_off, e['size'], nb, txt))
