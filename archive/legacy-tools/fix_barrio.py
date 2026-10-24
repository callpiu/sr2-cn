# -*- coding: utf-8 -*-
"""单独处理 0x4A19C：任务提示里内嵌的 'Barrio'"""
import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = '961330e67e70f70554f8062d62570866'

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
blob = v.read(v.find('static_CH', 'le_strings'))
CH_LO = ds + v.find('static_CH', 'le_strings')['body']

ENT = {}
for e in v.entries():
    ENT[e['name'] + '.' + e['ext']] = (ds + e['body'], ds + e['body'] + e['size'])

def owner(pos):
    for nm, (a, b) in ENT.items():
        if a <= pos < b:
            return nm
    return None

rel = 0x4A19C
text_at = CH_LO + rel + 4
term = text_at + 60 * 2

# 前置断言：记录起点前应是终止符，起点处是记录 ID
assert bytes(buf[text_at - 6:text_at - 4]) == b'\x00\x00', '前置终止符'
# 读旧 slot
old_slots = []
j = text_at
while j + 2 <= len(buf):
    x = struct.unpack_from('>H', buf, j)[0]
    if x == 0:
        break
    old_slots.append(x)
    j += 2
assert j == term, (hex(j), hex(term))
print('旧 slot 数', len(old_slots))
assert bytes(buf[j:j + 2]) == b'\x00\x00'

# 逐 slot 找 'Barrio' 的英文序列并替换为中文（尾部缩短）
OLD_B = b''.join(struct.pack('>H', S(c)) for c in 'Barrio')
NEW_B = b''.join(struct.pack('>H', S(c)) for c in '唐人街')
# 在记录内部找（从第 2 个 slot 起，因为前2 个是 ID 已在 text_at 之前）
old_b = bytes(buf[text_at:term])
assert old_b.count(OLD_B) == 1, old_b.count(OLD_B)
new_b = old_b.replace(OLD_B, NEW_B)
assert len(new_b) < len(old_b)

buf[text_at:term] = new_b + b'\x00' * (len(old_b) - len(new_b))

out = bytes(buf)
print()
print('其它语言表零改动断言:')
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'static_CH.le_strings':
        continue
    assert out[a:b] == orig[a:b], nm
print('   ★ 通过')
ch = sorted({nm for nm, (a, b) in ENT.items() if out[a:b] != orig[a:b]})
print('   实际修改条目:', ch)
assert len(out) == orig_len
open(P, 'wb').write(out)
print()
print('new md5', hashlib.md5(out).hexdigest())