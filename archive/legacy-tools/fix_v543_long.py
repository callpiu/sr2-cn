# -*- coding: utf-8 -*-
"""v543 补漏：两条含换行符的长任务提示（122 / 79 slot）里的Freckle Bitch's"""
import struct, hashlib, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = 'e45e4e81573b8428b5d63a10767e1b70'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def S(ch):
    return IDX[ord(ch)] + 0x20

buf = bytearray(open(P, 'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest() == BASE, 'baseline mismatch'
orig = bytes(buf)
orig_len = len(buf)

v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000
CH_LO = ds + v.find('static_CH', 'le_strings')['body']
ENT = {}
for e in v.entries():
    ENT[e['name'] + '.' + e['ext']] = (ds + e['body'], ds + e['body'] + e['size'])

def owner(pos):
    for nm, (a, b) in ENT.items():
        if a <= pos < b:
            return nm
    return None

OLD = "Freckle Bitch's"
NEW = '雀斑鸡'
old_b = b''.join(struct.pack('>H', S(c)) for c in OLD)
new_b = b''.join(struct.pack('>H', S(c)) for c in NEW)
assert len(new_b) < len(old_b)

TARGETS = [0x1A4FA, 0x6B9C6]     # blob 内相对偏移
n = 0
for rel in TARGETS:
    text_at = CH_LO + rel + 4
    # 定位记录终止符
    j = text_at
    cnt = 0
    while j + 2 <= len(buf):
        x = struct.unpack_from('>H', buf, j)[0]
        if x == 0:
            break
        cnt += 1
        j += 2
    # 允许穿过「上一条记录的终止符」继续找本条终止符：
    # 直接扫到「后面是 0000 且再后面是新记录」的第一个位置不安全，
    # 改用：slot 数与 CH 扫描一致（本处已知 122 / 79）
    want = {0x1A4FA: 122, 0x6B9C6: 79}[rel]
    assert cnt == want, (hex(rel), cnt, want)
    term = j
    assert bytes(buf[term:term + 2]) == b'\x00\x00'
    old_bytes = bytes(buf[text_at:term])
    assert old_bytes.count(old_b) == 1, (hex(rel), old_bytes.count(old_b))
    new_bytes = old_bytes.replace(old_b, new_b)
    assert len(new_bytes) < len(old_bytes)
    buf[text_at:term] = new_bytes + b'\x00' * (len(old_bytes) - len(new_bytes))
    n += 1
    print('  %08X  %d slot -> %d slot' % (text_at, len(old_bytes) // 2, len(new_bytes) // 2))

print('已改', n, '条')

out = bytes(buf)
print()
print('其它语言表零改动断言:')
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'static_CH.le_strings':
        continue
    assert out[a:b] == orig[a:b], nm
print('   ★ 通过')
print('   实际修改条目:', sorted({nm for nm, (a, b) in ENT.items() if out[a:b] != orig[a:b]}))
assert len(out) == orig_len
open(P, 'wb').write(out)
print()
print('new md5', hashlib.md5(out).hexdigest())