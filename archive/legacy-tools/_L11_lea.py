# -*- coding: utf-8 -*-
"""定位引用语言表 VA=0xDD1104 的代码（lea 指令，RIP相对/绝对立即数）。"""
import re
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000
TARGET=0xDD1104
for T in (0xDD1104, 0xDD1100, 0xDD10C4):
    b=T.to_bytes(4,'little')
    idxs=[m.start() for m in re.finditer(re.escape(b), raw[:0x9B8000])]
    print("被立即数引用 VA=0x%08X : %d 次 %s" % (T, len(idxs), [hex(i) for i in idxs[:12]]))
