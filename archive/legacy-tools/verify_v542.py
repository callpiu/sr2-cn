# -*- coding: utf-8 -*-
import struct, hashlib, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
P = G + 'patch.vpp_pc'
new = open(P, 'rb').read()
ob = open(G + 'patch.vpp_pc.before_v542.bak', 'rb').read()
print('md5', hashlib.md5(new).hexdigest())
print('size', len(new), '== old', len(ob), len(new) == len(ob))
print('diff bytes', sum(1 for i in range(len(new)) if new[i] != ob[i]))

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

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

v = Vpp(P)
CH = scan(v.read(v.find('static_CH', 'le_strings')))
allt = []
for off, o in CH:
    if len(o) > 2:
        allt.append((off, (o[0] << 16) | o[1], D(o[2:])))
print('CH records', len(CH))

print()
print('=== 残留检查（应全0）===')
for kw in ['圣徽街', 'Barrio', 'Rusty', 'PHUC MI', 'Technically Legal',
           'Elysian Fields', 'Sunsinger', 'Encanto']:
    n = sum(1 for o, h, x in allt if kw in x)
    print('   %-20s %d %s' % (kw, n, 'OK' if n == 0 else '★残留'))

print()
print('=== 新译名回读 ===')
for kw in ['圣徒街', '唐人街', '锈针', '福记面家', '法律边缘', '至乐田', '朝阳', '魔幻园']:
    n = sum(1 for o, h, x in allt if kw in x)
    print('   %-10s %d 条' % (kw, n))

print()
print('=== 前序版本回归 ===')
for kw, lo in [('市郊', 30), ('霰弹枪', 10), ('弹药', 35), ('三街圣徒', 40),
               ('兄弟会', 100), ('主城区', 20), ('注意', 10), ('取消', 30),
               ('帽衫镇', 1), ('昆比卡', 1), ('神奇超市', 1)]:
    n = sum(1 for o, h, x in allt if kw in x)
    print('   %-8s %-5d %s' % (kw, n, 'OK' if n >= lo else '★低'))

print()
print('=== voice_script / DLC 回归 ===')
import os
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)
def pk(s):
    return b''.join(struct.pack('>H', IDX[ord(c)] + 0x20) for c in s)
for nm, p in [('voice_script', G + 'DLC/Text/dlc_ch.le_strings')]:
    if os.path.exists(p):
        b = open(p, 'rb').read()
        print('   %s 父亲=%d 神父=%d' % (nm, b.count(pk('父亲')), b.count(pk('神父'))))
b = new
print('   整文件 父亲=%d 神父=%d' % (b.count(pk('父亲')), b.count(pk('神父'))))

print()
print('=== 其它语言表完整性 ===')
v3 = Vpp(P)
ds = v3.data_start if hasattr(v3, 'data_start') else 0x9000
ch = set()
for e in v3.entries():
    a = ds + e['body']; b2 = a + e['size']
    if new[a:b2] != ob[a:b2]:
        ch.add(e['name'] + '.' + e['ext'])
print('   实际修改条目:', sorted(ch))