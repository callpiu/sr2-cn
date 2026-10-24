# -*- coding: utf-8 -*-
"""生成修复版 charlist_CH.txt（带 count=2795 头，CRLF，风格同官方）。"""
import sys, re
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
raw=v.read(v.find('charlist_CH','txt'))
toks=[int(x) for x in raw.split() if x.lstrip(b'-').isdigit()]
N=len(toks)
print("当前项数 =", N)
hdr = ("//Used character list based on file 'd://projects//sr2//main//data//tables//localized_exports//platform_pc_CH.txt'\r\n"
       "// Appending to file 'd://projects//sr2//main//data//tables//localized_exports//charlist_CH.txt'\r\n"
       "// a list of all characters known to be used in Saint's Row.\r\n"
       "// used to compress from 65536 Unicode\r\n"
       "count=%d\r\n" % N)
body = "\r\n".join(str(t) for t in toks) + "\r\n"
out = (hdr + body).encode('latin1')
open('F:/sr2-cn/_fixed_charlist_CH.txt','wb').write(out)
print("已生成 _fixed_charlist_CH.txt: %d 字节" % len(out))
print(repr(out[:260]))
print("...")
print(repr(out[-40:]))
# 校验: 去注释项数
t2=[int(x) for x in out.split() if x.lstrip(b'-').isdigit()]
print("新文件数字 token 数 =", len(t2), "(应 = N+1 =", N+1, ")")
