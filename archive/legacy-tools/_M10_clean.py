# -*- coding: utf-8 -*-
"""去掉注释行，看各表的纯数据流开头。"""
import sys, re
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
for nm in ['charlist_CH','charlist_JP','charlist_CZ','charlist_SK','charlist_PL','charlist_RU','JPCharList']:
    raw=v.read(v.find(nm,'txt')).decode('latin1')
    lines=raw.splitlines()
    data=[]
    for ln in lines:
        s=ln.strip()
        if not s or s.startswith('//'): continue
        for tok in s.replace('\r',' ').split():
            if tok.lstrip('-').isdigit(): data.append(int(tok))
    print("=== %s: 去注释后 %d 项 ===" % (nm, len(data)))
    print("   前 14 项:", data[:14])
    print("   末 4 项 :", data[-4:])
    print()
