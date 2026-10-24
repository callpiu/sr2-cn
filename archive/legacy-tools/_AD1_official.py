# -*- coding: utf-8 -*-
import sys, struct, io, os, re, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

CASES = [
    ('common.official', r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc"),
    ('common.patched',  r"F:\sr2-cn\_backup_F\common.patched_20261013_174215_to_be_rolled_back.vpp_pc"),
    ('common.now',      r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc"),
    ('textures.official', r"F:\sr2-cn\_backup_E\textures.official_20261013_174215.vpp_pc"),
]
for tag, p in CASES:
    if not os.path.exists(p):
        print(tag, "MISSING"); continue
    v = Vpp(p)
    print("=== %s  entries=%d ===" % (tag, v.num))
    for e in v.entries():
        nm = (e['name'] + '.' + e['ext']).lower()
        if 'charlist' in nm or ('fnt_chinese' in nm) or 'fnt_body' in nm:
            d = v.read(e)
            extra = ''
            if 'charlist' in nm:
                cl = parse_plain(d)
                extra = 'count=%d 你idx=%s' % (len(cl), cl.index(0x4F60) if 0x4F60 in cl else None)
            print("   %-14s %-9s size=%-8d md5=%s  %s" %
                  (e['name'], e['ext'], len(d), hashlib.md5(d).hexdigest()[:12], extra))
