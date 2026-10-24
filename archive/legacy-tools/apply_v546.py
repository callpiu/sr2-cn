# -*- coding: utf-8 -*-
"""
v546：修OpenSpy（联机登录）界面的错位字
★根因：数据正确，但该界面渲染时「登/录/出」三个字位取错字形
   登(1865)→璃、录(1077)→傲、出(510)→兵
   同界面「在线/邮箱/密码/创建账号」正常 ⇒ 仅这三个字位坏
★修法：换成不含这三个字的等义词（连接/断开），全程等长或缩短
★范围：platform_pc_CH.le_strings（联机平台表）
"""
import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = '8d82233053e1231337eeb84c82d1933b'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def S(ch):
    assert ord(ch) in IDX, '字表缺字: %s' % ch
    return IDX[ord(ch)] + 0x20

def pack(s):
    return b''.join(struct.pack('>H', S(c)) for c in s)

buf = bytearray(open(P, 'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest() == BASE, 'baseline mismatch'
orig = bytes(buf)
orig_len = len(buf)

v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000
ENT = {}
for e in v.entries():
    ENT[e['name'] + '.' + e['ext']] = (ds + e['body'], ds + e['body'] + e['size'])

def owner(pos):
    for nm, (a, b) in ENT.items():
        if a <= pos < b:
            return nm
    return None

def allowed(pos):
    nm = owner(pos)
    return nm is None or nm == 'platform_pc_CH.le_strings'

# (ID, 旧文本, 新文本, 依据)
RULES = [
    (0x5396E11F, '登录 GameSpy', '连接 OpenSpy', 'Log into GameSpy → 截图显示「轻傲OpenSpy卧短」'),
    (0xAFEEEDA5, '退出 GameSpy', '断开 OpenSpy', 'Log out of GameSpy → 截图显示「璃兵」'),
    (0x96B1F720, '登录', '连接',  'Login → 主菜单显示「璃傲」'),
    (0xB54D5B12, '退出', '断开',  'Exit → 主菜单显示「璃兵」'),
]

print('=== 译名表 ===')
for hid, old, new, why in RULES:
    po, pn = pack(old), pack(new)
    mode = '缩短' if len(pn) < len(po) else ('等长' if len(pn) == len(po) else '★变长')
    print('  ID=%08X %-14r -> %-14r %d->%d slot  %s' % (hid, old, new,
          len(po) // 2, len(pn) // 2, mode))
    assert len(pn) <= len(po), 'ID=%08X 需扩容' % hid

PL_LO, PL_HI = ENT['platform_pc_CH.le_strings']
blob = v.read(v.find('platform_pc_CH', 'le_strings'))

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

def dec(slots):
    return ''.join(chr(x) if x < 0x20 else (chr(CL[x - 0x20]) if x - 0x20 < len(CL) else '?')
                   for x in slots)

by_id = {}
for off, o in scan(blob):
    if len(o) > 2:
        by_id.setdefault((o[0] << 16) | o[1], []).append((off, o))

n = 0
print()
print('=== 表内替换（按 ID 定位）===')
for hid, old, new, why in RULES:
    rows = by_id.get(hid)
    assert rows, 'ID=%08X 未找到' % hid
    for off, o in rows:
        text = dec(o[2:])
        assert text == old, 'ID=%08X 现文本 %r != %r' % (hid, text, old)
        n_slot = len(o) - 2
        nb = pack(new)
        assert len(nb) // 2 <= n_slot, 'ID=%08X 需扩容' % hid
        abs_text = PL_LO + off + 4
        assert bytes(buf[abs_text:abs_text + n_slot * 2]) == pack(old), '字节不匹配'
        assert bytes(buf[abs_text + n_slot * 2:abs_text + n_slot * 2 + 2]) == b'\x00\x00'
        buf[abs_text:abs_text + n_slot * 2] = nb + b'\x00' * (n_slot * 2 - len(nb))
        n += 1
        print('  %08X ID=%08X %r -> %r' % (abs_text, hid, old, new))

print()
print('=== 表外松散副本 ===')
done_abs = {PL_LO + off + 4 for off, o in scan(blob) if len(o) > 2}
for hid, old, new, why in RULES:
    pat = pack(old) + b'\x00\x00'
    nb = pack(new)
    k = 0
    while True:
        k = bytes(buf).find(pat, k)
        if k < 0: break
        if not allowed(k) or k in done_abs:
            k += 2; continue
        buf[k:k + len(pat)] = nb + b'\x00' * (len(pat) - len(nb))
        n += 1
        print('  %08X ID=%08X %r -> %r  (%s)' % (k, hid, old, new,
              owner(k) or '表外松散区'))
        k += len(nb)

print()
print('合计替换:', n, '处')

out = bytes(buf)
print()
print('=== 断言其它语言表零改动 ===')
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'platform_pc_CH.le_strings':
        continue
    assert out[a:b] == orig[a:b], nm
print('   ★ 通过')
changed = sorted({nm for nm, (a, b) in ENT.items() if out[a:b] != orig[a:b]})
print('   实际修改条目:', changed)
assert len(out) == orig_len
open(P, 'wb').write(out)
print()
print('size', len(out), '(unchanged)')
print('new md5', hashlib.md5(out).hexdigest())