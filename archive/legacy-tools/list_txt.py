# -*- coding: utf-8 -*-
"""列出 patch / common / city_load 里所有文本类条目，找 hood/district 名来源"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
for f,lbl in [(G+r'\patch.vpp_pc','patch'),
              (G+r'\common.vpp_pc','common'),
              (G+r'\city_load.vpp_pc','city_load')]:
    v=Vpp(f)
    print('=== %s  entries=%d'%(lbl,v.num))
    for e in v.entries():
        nm=e['name'].lower(); ex=e['ext'].lower()
        if ex in ('fxo_pc','vtf','g_peg_pc','dds','wav'): continue
        if ex in ('xtbl','txt','csv','lua','xml','ini','dat') or \
           any(k in nm for k in ('hood','district','zone','region','nhood','neighborhood')):
            print('   %-36s %-10s %d'%(e['name'],e['ext'],e['size']))
    print()