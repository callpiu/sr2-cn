# -*- coding: utf-8 -*-
import sys, struct, io, re, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

SRC = r"F:\sr2-cn\_patchsrc\patch.vpp_pc"
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"

def load(p):
    v = Vpp(p)
    return v

for tag, p in (('PATCHZIP', SRC), ('GAME', GAME)):
    v = load(p)
    print("=== %s  entries=%d ===" % (tag, v.num))
    for nm, ext in (('static_CH', 'le_strings'), ('charlist_CH', 'txt'),
                    ('fnt_chinese', 'vf3_pc'), ('fnt_chinese', 'g_peg_pc')):
        e = v.find(nm, ext)
        if not e:
            print("  %s.%s : NOT FOUND" % (nm, ext)); continue
        d = v.read(e)
        print("  %-14s %-9s size=%-8d md5=%s" % (nm, ext, len(d), hashlib.md5(d).hexdigest()[:12]))
        if nm == 'static_CH':
            i = d.find(bytes.fromhex('f284ed87'))
            if i >= 0:
                o = i + 4; sl = []
                while True:
                    x = struct.unpack_from('>H', d, o)[0]; o += 2
                    if x == 0: break
                    sl.append(x)
                print("      F284ED87 slots:", sl)
