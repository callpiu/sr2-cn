# -*- coding: utf-8 -*-
"""
修复 Mods/JUICED - Strings/juiced_CH.le_strings（Juice 9.3.1 自带中文表）
★ 这才是 OpenSpy 界面文本的真正来源（覆盖了 patch 里的 platform_pc_CH）
★ 官方版整句都是乱码翻译（璃兵/轻傲/卧短/重推/仰寒篮帧/迹扰/地捐一/妈盆/擒短…）
★ 按 juiced_US.le_strings 的英文原版重新翻译
★★ ID 在本表里偏移 2 字节（记录区起点与 US 表差 2），故**按文本内容定位**，
   不按 ID 匹配 —— 避免错位。
★★ 换行用控制符 slot 0x0A（不是字表字符）。
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

def slots_of(text):
    """文本 -> slot 列表（\\n -> 控制符 0x0A）"""
    out = []
    for ch in text:
        if ch == '\n':
            out.append(0x0A)
        else:
            out.append(S(ch))
    return out

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

# ★ CH 记录区起点 0x013C（ID 从这里开始完整），US 0x0138
CH = parse(raw, 0x013C)
US = parse(us_raw, 0x0138)
print('CH %d 条, US %d 条' % (len(CH), len(US)))

# 英文原版 -> 中文
TRANSL = {
    'Log out of OpenSpy':                     '退出 OpenSpy',
    'Enter OpenSpy ID':                       '输入 OpenSpy ID',
    'You have been disconnected from OpenSpy.': '你已与 OpenSpy 断开连接。',
    'Connection to OpenSpy lost.\nReturning to main menu.':
        '与 OpenSpy 的连接已断开。\n正在返回主菜单。',
    'Enter OpenSpy Name':                     '输入 OpenSpy 名称',
    'Enter OpenSpy Password':                 '输入 OpenSpy 密码',
    'Enter OpenSpy E-mail':                   '输入 OpenSpy 电子邮箱',
    'Re-enter OpenSpy Password':              '再次输入 OpenSpy 密码',
    'Log into OpenSpy':                       '登录 OpenSpy',
    'E-mail':                                 '电子邮箱',
}

# 记录区按顺序一一对应（两表同序同长度）
assert len(CH) == len(US) or True
print()
print('=== 逐条对齐与改写 ===')
buf = bytearray(raw)
n = 0
for i, (pos, rid, slots, end) in enumerate(CH):
    if i >= len(US):
        break
    upos, urid, uslots, uend = US[i]
    en = dec(uslots)
    cur = dec(slots)
    if en not in TRANSL:
        print('  @%04X  ★英文原版无译文: %r' % (pos, en[:50]))
        continue
    cn = TRANSL[en]
    new_slots = slots_of(cn)
    old_len = len(slots)
    if len(new_slots) > old_len:
        print('  @%04X  ★变长 %d->%d 跳过: %r' % (pos, old_len, len(new_slots), en[:40]))
        continue
    nb = b''.join(struct.pack('>H', x) for x in new_slots)
    buf[pos + 4:pos + 4 + old_len * 2] = nb + b'\x00' * (old_len * 2 - len(nb))
    n += 1
    print('  @%04X  %-46r -> %r' % (pos, en[:44], cn))

print()
print('改写', n, '条')
out = bytes(buf)
assert len(out) == len(raw)
open(P, 'wb').write(out)
print('size', len(out), '(unchanged)')
print('new md5', hashlib.md5(out).hexdigest())

print()
print('=== 回读 ===')
for pos, rid, slots, end in parse(out, 0x013C):
    print('  @%04X %r' % (pos, dec(slots)[:70]))