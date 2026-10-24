# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
raw = pv.read(pv.find("static_CH"))

rawcl = open(r'F:\sr2-cn\_cur_charlist.txt', 'rb').read()
m = re.search(rb'count=(\d+)\r?\n', rawcl)
cl = [int(x) for x in re.findall(rb'\d+', rawcl[m.end():])]
print("charlist count:", len(cl), "first 100:", cl[:100])

def slots_after(pos):
    """read u16 BE slots after the 4-byte hash at pos, stop on 0000"""
    out = []
    o = pos + 4
    while True:
        v = struct.unpack_from('>H', raw, o)[0]
        o += 2
        if v == 0:
            break
        out.append(v)
        if len(out) > 200:
            break
    return out

def decode(slots):
    s = []
    for v in slots:
        if v < 0x100:
            s.append(chr(v))
        elif v - 1 < len(cl):
            s.append(chr(cl[v - 1]))
        elif v < len(cl):
            s.append(chr(cl[v]))
        else:
            s.append('<OOR:%d>' % v)
    return ''.join(s)

for name, pat in (('F284ED87 字幕', b'\xf2\x84\xed\x87'),
                  ('5A5AA49A HUD', b'\x5a\x5a\xa4\x9a'),
                  ('1738DE48 HUD', b'\x17\x38\xde\x48'),
                  ('FB2E8DE7 HUD', b'\xfb\x2e\x8d\xe7')):
    i = raw.find(pat)
    sl = slots_after(i)
    print(name, "slots:", sl)
    print("   idx-1:", decode(sl))
