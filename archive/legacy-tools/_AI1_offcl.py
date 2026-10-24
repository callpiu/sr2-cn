# -*- coding: utf-8 -*-
import sys, struct, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

OFF = Vpp(r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc")
print("entries", OFF.num)
n_txt = 0
for e in OFF.entries():
    full = e['name'] + '.' + e['ext']
    if e['ext'].lower() in ('txt',) or 'list' in full.lower() or 'char' in full.lower():
        d = OFF.read(e)
        cl = parse_plain(d) if b'ENDOFFILE' in d or b'count=' in d[:200] else None
        print("  %-24s %-8s size=%-8d %s" % (e['name'], e['ext'], e['size'],
              ('count=%d' % len(cl)) if cl else d[:30]))
        n_txt += 1
print("txt-like entries:", n_txt)
