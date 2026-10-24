# -*- coding: utf-8 -*-
import sys, struct, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

# target: slot -> expected glyph codepoint
EXP = {403:0x4EFB, 1868:0x74A8, 1067:0x5076, 454:0x5DE7, 364:0x4F4D,
       2699:0x96C4, 2328:0x8861, 423:0x4F2A, 1222:0x8BE5}

TABLES = {}
for vfp in (r"F:\sr2-cn\_patchsrc\patch.vpp_pc",
            r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc",
            r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"):
    try:
        v = Vpp(vfp)
    except Exception as e:
        continue
    tag0 = os.path.basename(vfp)
    for e in v.entries():
        if 'charlist' in (e['name'] + e['ext']).lower():
            key = "%s:%s" % (tag0, e['name'])
            try:
                TABLES[key] = parse_plain(v.read(e))
            except Exception:
                pass
# also raw charlist.txt style search in common.vpp_pc entries containing numbers
print("tables found:", {k: len(v) for k, v in TABLES.items()})

def test(name, cl, mode):
    ok = 0
    for slot, cp in EXP.items():
        if mode == 'minus32':
            i = slot - 32
        elif mode == 'direct':
            i = slot
        elif mode == 'plus32':
            i = slot + 32
        else:
            i = slot
        c = cl[i] if 0 <= i < len(cl) else -1
        if c == cp:
            ok += 1
    return ok

for name, cl in TABLES.items():
    for mode in ('direct', 'minus32', 'plus32'):
        n = test(name, cl, mode)
        if n >= 2:
            print("*** MATCH %s mode=%s  %d/9" % (name, mode, n))
    print("%-40s %s" % (name, [test(name, cl, m) for m in ('direct','minus32','plus32')]))
