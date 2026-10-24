# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'F:/sr2-cn')
print("=== fontwork/charlist_final.bin (疑官方原版) 头部 ===")
raw=open('fontwork/charlist_final.bin','rb').read()
print(repr(raw[:400]))
print()
print("=== fontwork/charlist_new.bin 头部 ===")
raw2=open('fontwork/charlist_new.bin','rb').read()
print(repr(raw2[:400]))
print()
print("=== _archive/output_final/charlist_CH 头部 ===")
raw3=open('_archive/output_final/charlist_CH','rb').read()
print(repr(raw3[:200]))
print()
print("=== 当前 vpp 里 charlist_CH 头部(再次确认) ===")
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
r4=v.read(v.find('charlist_CH','txt'))
print(repr(r4[:200]))
