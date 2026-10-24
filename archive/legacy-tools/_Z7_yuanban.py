# -*- coding: utf-8 -*-
import sys, struct, io, re, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

FILES = {
    'JUICEFIX':   r"F:\sr2-cn\_src2\patch.vpp_pc",
    'YUANBAN':    r"F:\sr2-cn\_src2\patch.vpp_pc.原版对照",
    'ZIP1':       r"F:\sr2-cn\_patchsrc\patch.vpp_pc",
    'GAME':       r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc",
}
for tag, p in FILES.items():
    v = Vpp(p)
    e = v.find("charlist_CH", "txt")
    cl = parse_plain(v.read(e)) if e else []
    i_ni = cl.index(0x4F60) if 0x4F60 in cl else -1
    c371 = cl[371] if len(cl) > 371 else 0
    print("%-9s count=%-5d idx你=%-5d cl[371]=U+%04X(%s) has們=%s cl[403]=U+%04X" %
          (tag, len(cl), i_ni, c371, chr(c371) if c371 else '?', 0x5011 in cl,
           cl[403] if len(cl) > 403 else 0))
    se = v.find("static_CH", "le_strings")
    d = v.read(se)
    i = d.find(bytes.fromhex('f284ed87'))
    sl = []
    if i >= 0:
        o = i + 4
        while True:
            x = struct.unpack_from('>H', d, o)[0]; o += 2
            if x == 0: break
            sl.append(x)
    print("          static_CH size=%d F284ED87 slots[:6]=%s" % (len(d), sl[:6]))
