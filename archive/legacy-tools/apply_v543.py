# -*- coding: utf-8 -*-
"""
v542：补全店名/地名残留 + 圣徽街 → 圣徒街
★★★ 只改 static_CH.le_strings 及其【表外松散副本】，其它语言表零改动。

核心手法：整记录重建（record rebuild）
  le_strings 一条记录 = [ID 2slot][文本 slot...][0000]，文本是连续的 slot 数组。
  若在中途把 5 个英文 slot 换成 3 个中文 slot，其后所有 slot 都会前移错位。
  ⇒ 必须「解码整条 → 字符串替换 → 重新编码整条 → 尾部补 0000」。
  前提：① 该记录每个 slot 都能无损解码回 charlist 里的码点（否则不能重建）
        ② 新文本 slot 数 <= 旧 slot 数（只缩短不扩容）。
"""
import struct, hashlib, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = '4b787aa9d1fea0beebd20ae15feaa5f5'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)
REV = {}
for i, cp in enumerate(CL):
    REV.setdefault(cp, i)

def S(ch):
    assert ord(ch) in IDX, '字表缺字: %s' % ch
    return IDX[ord(ch)] + 0x20

CTRL = {}      # 占位符 -> slot
BACK = {}      # slot -> 占位符

def pack(s):
    """字符串 -> slot 字节；识别 \x01Cxx\x01 控制符占位符"""
    out = []
    i = 0
    while i < len(s):
        if s[i] == '\x01':
            j = s.index('\x01', i + 1)
            out.append(struct.pack('>H', BACK[s[i + 1:j]]))
            i = j + 1
        else:
            out.append(struct.pack('>H', S(s[i])))
            i += 1
    return b''.join(out)

def decode_slots(slots):
    """slot 列表 -> 字符串；控制字符用 \x01 起始的可打印占位，避免 chr(0x0A) 破坏字符串"""
    out = []
    for x in slots:
        if x == 0:
            return None            # 记录内不该有 0
        if x < 0x20:
            # 控制字符（空格/撇号/换行等）：保留占位符以便原样写回
            if x not in CTRL:
                CTRL[x] = '\x01C%02X\x01' % x
                BACK[x] = CTRL[x]
            out.append(CTRL[x])
        elif x - 0x20 < len(CL):
            out.append(chr(CL[x - 0x20]))
        else:
            return None
    return ''.join(out)

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
    return nm is None or nm == 'static_CH.le_strings'

# ============ 替换规则 ============
# (旧文本, 新文本)  —— 全部在整条记录的解码文本上做字符串替换
RULES = [
    ("Freckle Bitch's", '雀斑鸡'),      # 快餐店（含大小写与拼写变体）
    ("FRECKLE BITCH'S", '雀斑鸡'),
    ("Freckle Bitchs", '雀斑鸡'),
    ("APOLLO'S", '阿波罗餐厅'),          # 快餐店
    ('Ezpata', '埃斯帕塔'),           # 唐人街街区名（US 地名专名名录确认）
    ('Gaslamp', '煤气灯区'),           # 唐人街街区名（US 地名专名名录确认）
]

# 只处理「短记录」（<=24 slot）：任务提示等长句不值得为省事而冒险
MAX_SLOT = 120

def find_records():
    """找出所有含目标文本的记录，返回 [(abs_text_start, old_slots, old_text)]"""
    res = []
    data = bytes(buf)
    for old, new in RULES:
        # 找 slot 序列出现处（含前后终止符校验）
        pat = pack(old)
        k = 0
        while True:
            k = data.find(pat, k)
            if k < 0:
                break
            if not allowed(k):
                k += 2
                continue
            # 向前回溯到记录文本起点（ID 后）
            # 记录起点 = 文本起点 - 4；文本起点由 slot 序列位置反推
            # 做法：从 k 往前找 0000 终止符，+2 即为记录起点（ID 首 slot）
            st = k
            while st >= 4 and data[st - 2:st] != b'\x00\x00':
                st -= 2
                if k - st > 4 + MAX_SLOT * 2:
                    break
            if data[st - 2:st] != b'\x00\x00':
                k += 2
                continue
            rec_start = st                     # 记录起点（ID 首 slot）
            text_at = st + 4                   # 文本起点
            if text_at > k:
                k += 2
                continue
            # 读文本 slot 直到 0000
            j = text_at
            slots = []
            while j + 2 <= len(data):
                x = struct.unpack_from('>H', data, j)[0]
                if x == 0:
                    break
                slots.append(x)
                j += 2
            if len(slots) > MAX_SLOT:
                k += 2
                continue
            txt = decode_slots(slots)
            if txt is None:
                k += 2
                continue
            assert data[j:j + 2] == b'\x00\x00', '终止符异常 %08X' % text_at
            res.append((text_at, j, slots, txt, old, new))
            k = j
    return res

recs = find_records()
# 去重（同一 text_at 只保留一条）
seen = {}
for text_at, term, slots, txt, old, new in recs:
    seen[text_at] = (text_at, term, slots, txt)
recs = sorted(seen.values())

print('=== 待改记录（含内嵌片段）===')
plan = []
for text_at, term, slots, txt in recs:
    newtxt = txt
    for old, new in RULES:
        newtxt = newtxt.replace(old, new)
    if newtxt == txt:
        continue
    # 前提：所有新字符都在字表
    miss = sorted({c for c in newtxt if ord(c) not in IDX})
    if miss:
        print('   ★跳过 %08X 字表缺字 %s : %r' % (text_at, ''.join(miss), txt[:50]))
        continue
    if len(newtxt) > len(slots):
        print('   ★跳过 %08X 变长 %d>%d : %r' % (text_at, len(slots), len(newtxt), txt[:50]))
        continue
    plan.append((text_at, term, slots, txt, newtxt))

print()
for text_at, term, slots, txt, newtxt in plan:
    print('   %08X slot %-3d -> %-3d' % (text_at, len(slots), len(newtxt)))
    print('        旧: %r' % txt[:78])
    print('        新: %r' % newtxt[:78])

print()
print('合计待改记录:', len(plan))

# ============ 执行 ============
for text_at, term, slots, txt, newtxt in plan:
    old_bytes = bytes(buf[text_at:term])
    new_bytes = pack(newtxt)
    assert len(new_bytes) <= len(old_bytes)
    buf[text_at:term] = new_bytes + b'\x00' * (len(old_bytes) - len(new_bytes))
    # 断言终止符仍在
    assert bytes(buf[text_at + len(old_bytes):text_at + len(old_bytes) + 2]) == b'\x00\x00'

out = bytes(buf)
print()
print('=== 断言其它语言表零改动 ===')
for nm, (a, b) in ENT.items():
    if 'le_strings' not in nm or nm == 'static_CH.le_strings':
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