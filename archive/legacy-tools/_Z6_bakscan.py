# -*- coding: utf-8 -*-
import sys, struct, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
files = [f for f in os.listdir(G) if f.startswith('patch.vpp_pc')]
files.sort()
print("%-58s %6s %6s %6s %6s" % ("file", "count", "idx你", "cl371", "has們"))
for fn in files:
    p = os.path.join(G, fn)
    try:
        v = Vpp(p)
        e = v.find("charlist_CH", "txt")
        if not e:
            print("%-58s  (no charlist_CH)" % fn); continue
        cl = parse_plain(v.read(e))
        i_ni = cl.index(0x4F60) if 0x4F60 in cl else -1
        c371 = 'U+%04X' % cl[371] if len(cl) > 371 else '-'
        has_fan = 0x5011 in cl
        print("%-58s %6d %6d %6s %6s" % (fn, len(cl), i_ni, c371, has_fan))
    except Exception as ex:
        print("%-58s  ERR %s" % (fn, ex))
