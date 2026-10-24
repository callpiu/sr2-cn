# -*- coding: utf-8 -*-
"""从官方备份 vpp 里读原始 charlist_CH。"""
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
for p in [r'F:/sr2-cn/_backup_F/common.official_20261013_175139.vpp_pc']:
    v=Vpp(p)
    hits=[e for e in v.entries() if 'charlist' in (e['name']+e['ext']).lower()]
    print("%s: %d charlist" % (p, len(hits)))
    for e in hits:
        print("   ", e['name']+'.'+e['ext'])
