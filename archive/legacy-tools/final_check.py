# -*- coding: utf-8 -*-
"""回滚总校验"""
import sys, struct, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(ch): return IDX[ord(ch)]+0x20
def P(s): return struct.pack('>%dH'%len(s),*[S(c) for c in s])
b=open(PATCH,'rb').read()
print('size =',len(b),' md5 =',hashlib.md5(b).hexdigest())
for name,s in [('指定辩护人','指定辩护人'),('指定辩护律+sp','指定辩护律 '),('指定辩护律师','指定辩护律师'),
               ('兄弟帮','兄弟帮'),('兄弟会','兄弟会'),('3王','3王'),('三王','三王'),
               ('霰弹枪','霰弹枪'),('三街圣徒','三街圣徒'),('3rdS','3rdS')]:
    if name.endswith('+sp'):
        pat=struct.pack('>6H',S('指'),S('定'),S('辩'),S('护'),S('律'),0x20)
    else:
        pat=P(s)
    print('  %-12s = %d'%(name,b.count(pat)))