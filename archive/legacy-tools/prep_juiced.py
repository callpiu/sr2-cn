# -*- coding: utf-8 -*-
"""
修复 Mods/JUICED - Strings/juiced_CH.le_strings（Juice 9.3.1 自带中文表）
★ 这才是 OpenSpy 界面文本的真正来源（覆盖了 patch 里的 platform_pc_CH）
★ 官方版整句都是乱码翻译（璃兵/轻傲/卧短/重推/仰寒篮帧/迹扰/地捐一/妈盆/擒短…）
★ 按 juiced_US.le_strings 的英文原版重新翻译全部 11 条 + 1 条无英文对应的
★★ 结构（已破解）：
     头部 12B [magic u32][ver u16][buckets u16][count u32]
     桶表 buckets × [count u32][addr u32]     ← addr 指向指针数组项
     指针数组 count × u32                     ← 指向记录区绝对偏移
     记录区 [ID u32][文本 slot...][0000]
   扩容 = 重排记录区 + 更新指针数组；桶表 count 不变，无需改动。
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
    out = []
    for ch in text:
        out.append(0x0A if ch == '\n' else S(ch))
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

mCH = parse_tbl(raw)
mUS = parse_tbl(us_raw)
_, _, nB, nC, bkt, ptrs, CH = mCH
_, _, _, _, _, _, US = mUS
print('CH: buckets=%d count=%d | US: count=%d' % (nB, nC, len(US)))

us_by_id = {}
for i, rid, slots, off, end in US:
    us_by_id[rid] = dec(slots)

# ★★★ 完整译文（按 ID 精确对应）★★★
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
    # ★ CH 独有的一条（US 表无对应）：官方版是整句乱码
    #   '争掌?%i/%i?仰赃写乖[format][color:green]$%i[/format]?禁符?%ls'
    #   ★ 用 juiced_CH.cxt 里的同 ID 条目确认原文
    0x54559450: None,   # 稍后单独处理
}

print()
print('=== 逐条对照 ===')
for i, rid, slots, off, end in CH:
    en = us_by_id.get(rid, '★US无对应')
    cur = dec(slots)
    cn = TRANSL.get(rid)
    print('  [%2d] ID=%08X slots=%-3d' % (i, rid, len(slots)))
    print('        US=%r' % en[:56])
    print('        现=%r' % cur[:56])
    print('        新=%r' % (cn if cn is not None else '(待定)'))

json_out = {}
for i, rid, slots, off, end in CH:
    cn = TRANSL.get(rid)
    if cn is not None:
        json_out['%08X' % rid] = cn
import json
json.dump(json_out, open('F:/sr2-cn/_juiced_transl.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)