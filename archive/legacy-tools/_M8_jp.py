# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
for nm in ['charlist_JP','charlist_CZ','charlist_SK','JPCharList','charlist_CH']:
    raw=v.read(v.find(nm,'txt'))
    print("=== %s (raw %d bytes) ===" % (nm, len(raw)))
    print("  前 160 字节:", raw[:160])
    txt=raw.decode('latin1','replace')
    ns=[int(t) for t in raw.split() if t.lstrip(b'-').isdigit()] if False else None
    import re
    ns=[int(x) for x in re.findall(rb'\d+', raw)]
    print("  数值项数=%d 前12=%s" % (len(ns), ns[:12]))
    print()
