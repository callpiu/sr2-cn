# -*- coding: utf-8 -*-
"""
v542：修复 Mods/JUICED - Strings/juiced_CH.le_strings（Juice 9.3.1 自带中文表）
★ 这才是 OpenSpy 界面文本的真正来源（覆盖了 patch 里的 platform_pc_CH）
★ 官方版整句都是乱码翻译（璃兵/轻傲/卧短/重推/仰寒篮帧/迹扰/地捐一/妈盆/擒短…）
★ 按 juiced_US.le_strings 的英文原版重新翻译全部 12 条
★★ 结构（已破解）：
     头部 12B [magic u32][ver u16][buckets u16][count u32]
     桶表 buckets × [count u32][addr u32]    ← addr 指向指针数组项
     指针数组 count × u32                    ← 指向记录区绝对偏移
     记录区 [ID u32][文本 slot...][0000]
   扩容 = 重排记录区 + 更新指针数组；桶表 count 不变，无需改。
"""
import struct, hashlib, sys, os

DIR = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/'
P = DIR + 'juiced_CH.le_strings'
US = DIR + 'juiced_US.le_strings'
BASE = 'ea20ee64f30cfe9847aa83b6946c1cda'

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
    return [0x0A if ch == '\n' else S(ch) for ch in text]

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

def parse_tbl(b):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', b, 0)
    p = 12
    buckets_tbl = []
    for i in range(buckets):
        c, a = struct.unpack_from('<II', b, p + i * 8)
        buckets_tbl.append((c, a))
    p += buckets * 8
    ptrs = [struct.unpack_from('<I', b, p + i * 4)[0] for i in range(count)]
    p += count * 4
    recs = []
    for i, off in enumerate(ptrs):
        rid = struct.unpack_from('<I', b, off)[0]
        j = off + 4
        slots = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            slots.append(x); j += 2
        recs.append((i, rid, slots, off, j + 2))
    return magic, ver, buckets, count, buckets_tbl, ptrs, recs

magic, ver, nB, nC, bkt, ptrs, CH = parse_tbl(raw)
_, _, _, _, _, _, US = parse_tbl(us_raw)
us_by_id = {rid: dec(slots) for i, rid, slots, off, end in US}

TRANSL = {
    0xA5EDEEAF: '退出 OpenSpy',
    0xC6EC1896: '输入 OpenSpy ID',
    0x2840CF1D: '再次输入 OpenSpy 密码',
    0x4BFF620D: '你已与 OpenSpy 断开连接。',
    0x2E971EEE: '与 OpenSpy 的连接已断开。\n正在返回主菜单。',
    0x70F326B6: '输入 OpenSpy 名称',
    0xD3305375: '电子邮箱',
    0x55709960: '输入 OpenSpy 密码',
    0x3E2123B9: '输入 OpenSpy 电子邮箱',
    0xDECC9455: '再次输入 OpenSpy 密码',
    0x1FE19653: '登录 OpenSpy',
    # ★ MP_SERVER_IP：服务器地址提示。原：'争掌?%i/%i?仰赃写乖[format]...$%i[/format]?禁符?%ls'
    #   格式标签与 %i/%i 保持原样，只把乱码中文换掉
    0x54559450: 'IP 地址 %i/%i 服务器[format][color:green]$%i[/format] 端口 %ls',
}

print('=== 字表检查 ===')
miss = sorted({c for cn in TRANSL.values() for c in cn if ord(c) not in IDX})
print('缺字:', miss if miss else '无')

# ===== 重建记录区 =====
print()
print('=== 重建记录区 ===')
new_records = []
for i, rid, slots, off, end in CH:
    cn = TRANSL.get(rid)
    if cn is None:
        print('  ★无译文，保持原样: ID=%08X' % rid)
        new_records.append((rid, slots))
        continue
    ns = slots_of(cn)
    print('  ID=%08X %2d slot -> %2d slot  %r' % (rid, len(slots), len(ns), cn[:46]))
    new_records.append((rid, ns))

# 组装：头部 + 桶表 + 指针数组 + 记录区
HDR = 12
BKT = nB * 8
PTR = nC * 4
rec_area = bytearray()
new_ptrs = []
base = HDR + BKT + PTR
for rid, slots in new_records:
    new_ptrs.append(base + len(rec_area))
    rec_area += struct.pack('<I', rid)
    for x in slots:
        rec_area += struct.pack('>H', x)
    rec_area += b'\x00\x00'      # 终止符

out = bytearray()
out += raw[:HDR]                                    # 头部（含 count，不变）
out += raw[HDR:HDR + BKT]                          # 桶表（原样，不改）
for p in new_ptrs:                                  # 指针数组（更新）
    out += struct.pack('<I', p)
out += rec_area

print()
print('原 size %d -> 新 size %d' % (len(raw), len(out)))
open(P, 'wb').write(bytes(out))
print('new md5', hashlib.md5(bytes(out)).hexdigest())

# ===== 回读验证 =====
print()
print('=== 回读验证 ===')
_, _, nb2, nc2, bk2, pt2, CH2 = parse_tbl(bytes(out))
assert len(CH2) == nC
for i, rid, slots, off, end in CH2:
    print('  [%2d] ID=%08X %r' % (i, rid, dec(slots)[:64]))

print()
print('=== 残留乱码检查 ===')
for bad in ['璃兵', '轻傲', '卧短', '重推', '仰寒篮帧', '迹扰', '地捐一',
            '哄写丹逼吾一', '妈盆', '擒短', '零粉', '争掌', '仰赃写乖', '禁符']:
    n = bytes(out).count(pack_bad := b''.join(struct.pack('>H', S(c)) for c in bad)) if all(
        ord(c) in IDX for c in bad) else 0
    print('  %-8s %d %s' % (bad, n, 'OK' if n == 0 else '★残留'))