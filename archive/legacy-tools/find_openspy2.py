# -*- coding: utf-8 -*-
"""
在 platform_pc_CH 里穷举所有可能对应截图的记录：
截图上主菜单有「璃傲OpenSpy」「璃兵」，登录框标题「轻傲OPENSPY卧短」
说明这两条文本含「OpenSpy」字样，但表里 slot 搜不到 OpenSpy
⇒ 可能 OpenSpy 在表里是「Open」+「Spy」分开的 slot，或是别的表
"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def dec(sl):
    out = []
    for x in sl:
        if x < 0x20: out.append(chr(x))
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

# 1) 所有 le_strings 表里找 Open / Spy 组合
print('=== 各 le_strings 表里含 Open 或 Spy 的记录 ===')
for e in v.entries():
    if e['ext'] != 'le_strings':
        continue
    blob = v.read(e)
    R = scan(blob)
    hits = []
    for off, o in R:
        if len(o) < 3: continue
        t = dec(o[2:])
        if re.search(r'Open|Spy|SPY|OPEN', t):
            hits.append((off, (o[0] << 16) | o[1], t))
    if hits:
        print('  %s: %d 条' % (e['name'], len(hits)))
        for off, h, t in hits[:12]:
            print('     %08X ID=%08X %r' % (off, h, t[:56]))

# 2) 穷举 platform_pc_CH 里所有 2-4 字的中文短词，列出候选
print()
print('=== platform_pc_CH 全部 2 slot 记录 ===')
R = scan(v.read(v.find('platform_pc_CH', 'le_strings')))
for off, o in R:
    if len(o) == 4:
        t = dec(o[2:]).strip()
        print('  %08X ID=%08X %r' % (off, (o[0] << 16) | o[1], t))