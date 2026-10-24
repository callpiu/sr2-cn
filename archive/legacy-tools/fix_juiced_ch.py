# -*- coding: utf-8 -*-
"""
修复 Mods/JUICED - Strings/juiced_CH.le_strings 里的 OpenSpy 界面错字
★ 这才是真正的数据源（Juice 自带的中文表，覆盖了 platform_pc_CH）
结构：记录区 = 若干 [ID 4B][文本 slot...][0000]
"""
import struct, hashlib, sys, os, re

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/juiced_CH.le_strings'
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
buf = bytearray(raw)
orig = bytes(buf)

# ===== 定位记录区：找第一个能自洽的记录起点 =====
REC_START = 0x0136

def parse_records(b):
    recs = []
    pos = REC_START
    while pos + 6 <= len(b):
        rid = struct.unpack_from('<I', b, pos)[0]
        j = pos + 4
        slots = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0:
                break
            slots.append(x)
            j += 2
        if b[j:j + 2] != b'\x00\x00':
            break
        recs.append((pos, rid, slots, j + 2))
        pos = j + 2
    return recs

recs = parse_records(bytes(buf))
print('=== juiced_CH.le_strings 全部记录 (%d 条) ===' % len(recs))
for pos, rid, slots, end in recs:
    print('  @%04X ID=%08X slots=%-3d %r' % (pos, rid, len(slots), dec(slots)[:56]))

# ===== 译名表：只改错字部分，英文 OpenSpy 保留 =====
# 错字 → 正确词（等长或更短，尾部补 0000 提前终止）
FIX = {
    '璃兵': '退出',   # 2→2 等长
    '轻傲': '登录',   # 2→2 等长
    '卧短': '',       # 2→0 缩短（删去）
}
print()
print('=== 修复表 ===')
for a, b in FIX.items():
    print('  %-6r -> %r' % (a, b))

# 逐条处理
n = 0
for pos, rid, slots, end in recs:
    text = dec(slots)
    new_slots = list(slots)
    changed = False
    for bad, good in FIX.items():
        bad_slots = [S(c) for c in bad]
        # 在 slots 里找连续匹配
        for i in range(len(new_slots) - len(bad_slots) + 1):
            if new_slots[i:i + len(bad_slots)] == bad_slots:
                repl = [S(c) for c in good]
                new_slots = new_slots[:i] + repl + new_slots[i + len(bad_slots):]
                changed = True
                break
    if not changed:
        continue
    old_len = len(slots)
    new_len = len(new_slots)
    assert new_len <= old_len, 'ID=%08X 变长' % rid
    nb = b''.join(struct.pack('>H', x) for x in new_slots)
    # 写回：文本区 + 终止符
    buf[pos + 4:pos + 4 + old_len * 2] = nb + b'\x00' * (old_len * 2 - len(nb))
    n += 1
    print('  @%04X ID=%08X %r -> %r' % (pos, rid, text[:40], dec(new_slots)[:40]))

print()
print('修改记录数:', n)

out = bytes(buf)
assert len(out) == len(orig), '长度变了！'
# 其它记录未变（除改动的）
open(P, 'wb').write(out)
print('size', len(out), '(unchanged)')
print('new md5', hashlib.md5(out).hexdigest())

# 回读
print()
print('=== 回读验证 ===')
for pos, rid, slots, end in parse_records(out):
    t = dec(slots)
    if 'OpenSpy' in t:
        print('  @%04X ID=%08X %r' % (pos, rid, t[:60]))
for bad in FIX:
    cnt = out.count(pack(bad))
    print('  残留 %-4r : %d' % (bad, cnt))