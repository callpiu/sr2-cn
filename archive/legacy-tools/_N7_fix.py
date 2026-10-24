# -*- coding: utf-8 -*-
"""修复 charlist_CH.txt：补上 count=N 头。
先精确计算当前表项数，再生成修复版。
"""
import sys, re, os
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

v=Vpp(G+'/patch.vpp_pc')
raw=v.read(v.find('charlist_CH','txt'))
print("当前 charlist_CH: %d 字节" % len(raw))
print("  前 60:", raw[:60])
# 精确项数
toks=[int(x) for x in raw.split() if x.lstrip(b'-').isdigit()]
print("  项数 =", len(toks))
print("  首项 =", toks[0], " 末项 =", toks[-1])
print("  是否已含 count= :", b'count=' in raw)

# 官方对照
vo=Vpp(r'F:/sr2-cn/vpp_backup/patch.vpp_pc.orig')
ro=vo.read(vo.find('charlist_CH','txt'))
toks_o=[int(x) for x in ro.split() if x.lstrip(b'-').isdigit()]
m=re.search(rb'count=(\d+)', ro)
print("\n官方 charlist_CH:")
print("  count= 声明 =", m.group(1).decode())
print("  去注释后项数 =", len(toks_o))
print("  首行内容:", ro.split(b'\r\n count=')[0][:200] if b'\r\ncount=' in ro else ro[:200])
