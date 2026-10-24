# -*- coding: utf-8 -*-
"""最后一搏: 检查是否有"4795项"或更大的 charlist 藏在别处(DFEngine/Juiced目录)"""
import os, glob, re
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
print("=== 搜 Juiced 目录 / data 目录下的表 ===")
for root in ['Juiced','data','DLC']:
    p=os.path.join(G,root)
    if not os.path.isdir(p): continue
    for dp,dn,fn in os.walk(p):
        for f in fn:
            if 'har' in f.lower() or 'list' in f.lower():
                fp=os.path.join(dp,f)
                print("  ", fp, os.path.getsize(fp))
print()
print("=== 游戏根目录所有 .txt ===")
for f in glob.glob(os.path.join(G,'*.txt')):
    print("  ", os.path.basename(f), os.path.getsize(f))
print()
# 检查 DFEngine 是否含 charlist 名
raw=open(G+'/DFEngine.dll','rb').read()
print("DFEngine 含 'charlist':", b'charlist' in raw)
print("DFEngine 含 'CH':", raw.count(b'CH'))
# 找 DFEngine 里的宽字符 charlist
w=b'c\x00h\x00a\x00r\x00l\x00i\x00s\x00t\x00'
print("DFEngine 宽字符 charlist:", b'charlist' in raw or w in raw)
