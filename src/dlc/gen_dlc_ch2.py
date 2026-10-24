# -*- coding: utf-8 -*-
"""生成修复版 dlc_ch.le_strings —— slot 编码版（2026-10-08 17:5x 定案）

★ 关键修正：DLC le_strings 的文本区与本体一样是【slot = 字表索引+0x20】机制，
  不是真 Unicode 码点！证据：官方 dlc_jp 最大码点仅 0x07CF（日文字表索引），
  「Warehouse」只有 2 字符（倉庫）。英文版 slot 恰好等于 ASCII 码点
  （字表前 95 项 = ASCII 32..126），故此前误判。
  写入真 CJK 码点 → 引擎按 slot 解 → 索引越界 → 实机显示空白（用户已实测）。

编码规则：
  '\\n'(0x0A) 原样保留（官方 us 亦然）
  其余字符查 charlist_CH（2795 项）：slot = 首个索引 + 0x20
"""
import sys, struct
sys.path.insert(0, r'F:/sr2-cn')
from sr2lib import Vpp
from rebuild4 import load, build, G
from translations_dlc import T

OUT = 'dlc_ch_new.le_strings'

# ---- 字表 ----
v = Vpp(r'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc')
e = [x for x in v.entries() if x['name'].lower() == 'charlist_ch'][0]
cps = [int(l) for l in v.read(e).decode('utf-8').split('\n') if l.strip().isdigit()]
assert cps[:95] == list(range(32, 127)), '字表 ASCII 头部异常'
cp2slot = {}
for i, cp in enumerate(cps):
    cp2slot.setdefault(cp, i + 0x20)
SLOT_MAX = len(cps) - 1 + 0x20
print('字表 %d 项  slot 上限 0x%X  重复码点 %d 个'
      % (len(cps), SLOT_MAX, len(cps) - len(cp2slot)))

NEWLINE = 0x0A

def encode(text):
    out = []
    for c in text:
        o = ord(c)
        if o == NEWLINE:
            out.append(NEWLINE)
            continue
        s = cp2slot.get(o)
        if s is None:
            raise KeyError('缺字 U+%04X %r' % (o, c))
        out.append(s)
    return out

def decode(slots):
    out = []
    for s in slots:
        if s == NEWLINE:
            out.append('\n')
            continue
        i = s - 0x20
        assert 0 <= i < len(cps), 'slot 越界 0x%X' % s
        out.append(chr(cps[i]))
    return ''.join(out)

# ---- 译文 ----
ru, Nu, A0, T0, buckets, arr, entsu = load(G + 'dlc_us.le_strings')
rc, Nc, A0c, T0c, bkc, arrc, entsc = load(G + 'dlc_ch.le_strings')   # 当前部署(码点版)：795 条中文在此
du = dict(entsu)
dc = dict(entsc)
new_text = {}
n_from_ch = n_from_T = 0
for h, et in entsu:
    key = '%08X' % h
    if key in T:
        new_text[h] = T[key]; n_from_T += 1      # 补译/改写版优先
    else:
        assert h in dc and dc[h] != et, '缺少译文 %08X %s' % (h, et[:40])
        new_text[h] = dc[h]; n_from_ch += 1
print('译文 %d 条（旧ch %d + 新补 %d）' % (len(new_text), n_from_ch, n_from_T))

# 编码 + 回读校验
enc = {}
for h, t in new_text.items():
    sl = encode(t)
    assert decode(sl) == t, 'roundtrip 失败 %08X' % h
    enc[h] = sl
print('全部 %d 条编码并回读校验通过' % len(enc))

# 槽位与英文原文长度可不同（记录可变长）——但标记数量必须一致
for h, t in new_text.items():
    et = du[h]
    assert et.count('[format]') == t.count('[format]') and \
           et.count('[/format]') == t.count('[/format]') and \
           et.count('%ls') == t.count('%ls') and \
           et.count('%d') == t.count('%d'), '标记不一致 %08X' % h
    assert et.startswith('[image:') == t.startswith('[image:'), 'image 前缀不一致 %08X' % h
print('标记/占位符一致性通过')

# ---- 写入记录区（slot u16 BE）----
from rebuild4 import ptr_map as r4_ptr_map, derive as r4_derive
pm_us = r4_ptr_map(entsu, T0)
slot_k, miss_k = r4_derive(arr, pm_us)          # 数组下标 -> hash（保持原版数组顺序）
assert not miss_k
body = bytearray()
pos = {}
for h in [h for h, _ in entsu]:
    pos[h] = T0 + len(body)
    body += struct.pack('>I', h)
    body += b''.join(struct.pack('>H', s) for s in enc[h])
    body += b'\x00\x00'

out_arr = b''.join(struct.pack('<I', pos[slot_k[k]]) for k in range(Nu))
out = bytes(ru[:A0]) + out_arr + bytes(body)
open(OUT, 'wb').write(out)
print('已生成 %s  %d 字节' % (OUT, len(out)))

# ---- 独立复核 ----
rv, Nv, A0v, T0v, bv, arrv, entsv = load(OUT)
print('复核: N=%d TEXT0=0x%X  头部与us相同=%s  桶表与us相同=%s'
      % (Nv, T0v, rv[:A0v] == ru[:A0v], bv == buckets))
d = dict(entsv)
def decode2(s):          # load() 返回的文本是 chr(u16)，ord 还原后按 slot 解
    return decode([ord(c) for c in s])
ok = all(decode2(d[h]) == new_text[h] for h in new_text)
print('复核: 982 条逐条 slot 解码与译文一致 =', ok)
vals = [ord(c) for h, s in entsv for c in s]
print('复核: 全部槽位 ≤0x%X 或为换行 = %s' % (SLOT_MAX, all(u <= SLOT_MAX or u == NEWLINE for u in vals)))
pm2 = {}
o = T0v
for h, s in entsv:
    pm2[o] = h
    o += 4 + 2 * len(s) + 2
hit = sum(1 for a in arrv if a in pm2)
print('复核: 指针命中 %d/%d' % (hit, Nv))
# 数组顺序与原版一致：新数组下标 k 指向的 hash == 原数组下标 k 的 hash
pv2 = {}
o = T0v
for h, s in entsv:
    pv2[o] = h
    o += 4 + 2 * len(s) + 2
same_order = all(pv2[arrv[k]] == slot_k[k] for k in range(Nv))
print('复核: 数组下标→hash 顺序与原版完全一致 =', same_order)
for hh in (0x0E58435C, 0x3342D5FC, 0x22C8F187):
    print('   %08X -> %s' % (hh, decode2(d[hh])[:50]))
