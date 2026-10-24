# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

vo = Vpp(r'F:\sr2-cn\vpp_backup\patch.vpp_pc.orig')
ro = vo.read(vo.find('charlist_CH', 'txt'))
print("官方 charlist_CH: %d 字节" % len(ro))
print("含 //ENDOFFILE :", b'//ENDOFFILE' in ro)
i = ro.find(b'//ENDOFFILE')
print("ENDOFFILE 位置:", i, " 距末尾:", len(ro) - i)
print("ENDOFFILE 附近:", repr(ro[max(0, i - 30):i + 30]))
print()
print("行尾类型: CRLF=%d  LF单独=%d" % (ro.count(b'\r\n'), ro.count(b'\n') - ro.count(b'\r\n')))
print()
# 当前补丁
G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
r2 = v.read(v.find('charlist_CH', 'txt'))
print("当前补丁 charlist_CH: %d 字节" % len(r2))
print("含 //ENDOFFILE :", b'//ENDOFFILE' in r2)
print("行尾: CRLF=%d LF=%d" % (r2.count(b'\r\n'), r2.count(b'\n') - r2.count(b'\r\n')))
print("末尾 40 字节:", repr(r2[-40:]))
