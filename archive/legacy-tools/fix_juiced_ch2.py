# -*- coding: utf-8 -*-
"""
修复 Mods/JUICED - Strings/juiced_CH.le_strings（Juice 9.3.1 自带中文表）
★ 这才是 OpenSpy 界面文本的真正来源（覆盖了 platform_pc_CH）
★ 官方版整句都是「乱码翻译」（璃兵/轻傲/卧短/重推/仰寒篮帧/迹扰/地捐一/妈盆/擒短…）
★ 按 juiced_US.le_strings 的英文原版重新翻译全部 12 条
结构：记录区 = 若干 [ID 4B][文本 slot...][0000]
"""
import struct, hashlib, sys, os, re

DIR = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/'
P = DIR + 'juiced_CH.le_strings'
US = DIR + 'juiced_US.le_strings'
BASE = 'ea20ee64f30cfe9847aa83b6946c1cda'   # Juice 9.3.1 官方原版

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

def dec(sl):
    out = []
    for x in sl:
        if 0x20 <= x < 0x7f: out.append(chr(x))
        elif x < 0x20: out.append('^%02X' % x)
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

raw = open(P, 'rb').read()
assert hashlib.md5(raw).hexdigest() == BASE, 'baseline mismatch'
us_raw = open(US, 'rb').read()

def parse(b, st):
    recs = []
    pos = st
    while pos + 6 <= len(b):
        rid = struct.unpack_from('<I', b, pos)[0]
        j = pos + 4
        slots = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            slots.append(x); j += 2
        if b[j:j + 2] != b'\x00\x00':
            break
        recs.append((pos, rid, slots, j + 2))
        pos = j + 2
    return recs

CH = parse(raw, 0x013A)
US = parse(us_raw, 0x013A)
usd = {}
for pos, rid, slots, end in US:
    usd[rid] = dec(slots)
print('CH %d 条, US %d 条' % (len(CH), len(US)))

# ★★★ 逐条新译文（英文原版 → 正确中文）★★★
NEW = [
    # (ID, 英文原版, 新中文)
    (0xA5EDEEAF, 'Log out of OpenSpy',        '退出 OpenSpy'),
    (0x9618ECC6, 'Enter OpenSpy ID',          '输入 OpenSpy ID'),
    (0x4BFF620D, 'You have been disconnected from OpenSpy.',   '你已与 OpenSpy 断开连接。'),
    (0x2E971EEE, 'Connection to OpenSpy lost.\nReturning to main menu.',
     '与 OpenSpy 的连接已断开。\n正在返回主菜单。'),
    (0x70F326B6, 'Enter OpenSpy Name',        '输入 OpenSpy 名称'),
    (0x55709960, 'Enter OpenSpy Password',    '输入 OpenSpy 密码'),
    (0x3E2123B9, 'Enter OpenSpy E-mail',      '输入 OpenSpy 电子邮箱'),
    (0xDECC9455, 'Re-enter OpenSpy Password', '再次输入 OpenSpy 密码'),
    (0x1FE19653, 'Log into OpenSpy',          '登录 OpenSpy'),
    (0xD3305375, 'E-mail',                    '电子邮箱'),
]
print()
print('=== 译名表 ===')
for h, en, cn in NEW:
    print('  ID=%08X  %-46r -> %r' % (h, en[:44], cn))

# 字表检查
print()
miss = sorted({c for _, _, cn in NEW for c in cn if ord(c) not in IDX})
print('字表缺字:', miss if miss else '无')

# ===== 应用 =====
# 用「英文原版」定位：CH 里对应记录若已含错字，按 ID 匹配
buf = bytearray(raw)
n = 0
for pos, rid, slots, end in CH:
    hit = None
    for h, en, cn in NEW:
        if rid == h or (rid & 0xFFFFFF) == (h & 0xFFFFFF):
            hit = (h, en, cn); break
    if not hit:
        # 用文本匹配兜底
        t = dec(slots)
        for h, en, cn in NEW:
            if t.startswith(cn[:2]) or t.startswith('退出') or t.startswith('登录'):
                hit = (h, en, cn); break
    if not hit:
        continue
    h, en, cn = hit
    new_slots = [S(c) for c in cn]
    # 保留控制符（^0A 之类）：从旧 slots 里挑出来放在对应位置
    old_len = len(slots)
    if len(new_slots) > old_len:
        print('  ★跳过 ID=%08X（变长 %d->%d）' % (rid, old_len, len(new_slots)))
        continue
    nb = b''.join(struct.pack('>H', x) for x in new_slots)
    buf[pos + 4:pos + 4 + old_len * 2] = nb + b'\x00' * (old_len * 2 - len(nb))
    n += 1
    print('  @%04X ID=%08X %r -> %r' % (pos, rid, dec(slots)[:36], cn))

print()
print('修改', n, '条')
out = bytes(buf)
assert len(out) == len(raw)
open(P, 'wb').write(out)
print('size', len(out), '(unchanged)')
print('new md5', hashlib.md5(out).hexdigest())

print()
print('=== 回读 ===')
for pos, rid, slots, end in parse(out, 0x013A):
    print('  @%04X ID=%08X %r' % (pos, rid, dec(slots)[:64]))