# -*- coding: utf-8 -*-
"""生成修复版 dlc_ch.le_strings：
  1. 以现有 ch 的 795 条译文为基础
  2. 补译 translations_dlc.py 中剩余条目
  3. 按 us 的数组顺序重建 982 条指针（桶表/头部零改动）
"""
import struct
from rebuild4 import load, ptr_map, derive, build, G
from translations_dlc import T

OUT = 'dlc_ch_new.le_strings'

ru, Nu, A0, T0, buckets, arr, entsu = load(G + 'dlc_us.le_strings')
rc, Nc, A0c, T0c, bkc, arrc, entsc = load(G + 'dlc_ch.le_strings')
du = dict(entsu)
dc = dict(entsc)

new_text = {}
missing_src = []
for h, et in entsu:
    cn = dc.get(h)
    if cn is not None and cn != et:
        new_text[h] = cn          # 已有译文
    elif '%08X' % h in T:
        new_text[h] = T['%08X' % h]   # 本轮补译
    else:
        missing_src.append((h, et))

print('新译文覆盖 %d / %d' % (len(new_text), Nu))
if missing_src:
    print('仍缺 %d 条:' % len(missing_src))
    for h, t in missing_src[:20]:
        print('   %08X %s' % (h, t[:80]))

# 标记一致性检查：[format] 计数与 %ls 占位符必须保留
bad = []
for h, nt in new_text.items():
    et = du[h]
    if et.count('[format]') != nt.count('[format]') or \
       et.count('[/format]') != nt.count('[/format]') or \
       et.count('%ls') != nt.count('%ls'):
        bad.append(h)
    if et.startswith('[image:') != nt.startswith('[image:'):
        bad.append(h)
print('标记不一致条目:', bad if bad else '无')

out, _ = build(ru, Nu, A0, buckets, arr, entsu, new_text)
open(OUT, 'wb').write(out)
print('已生成 %s  %d 字节 (原 ch %d / 原 us %d)' % (OUT, len(out), len(rc), len(ru)))

# ---- 独立复核：用 load() 重新解析产物 ----
rv, Nv, A0v, T0v, bv, arrv, entsv = load(OUT)
print('复核: N=%d TEXT0=0x%X 头部0..0x40C与us相同=%s' % (Nv, T0v, rv[:A0v] == ru[:A0]))
print('复核: hash 集合与us一致=%s  桶表与us一致=%s' % (
    set(h for h, _ in entsv) == set(h for h, _ in entsu), bv == buckets))
# 指针必须全部命中本文件记录起点
pm = ptr_map(entsv, T0v)
slot, miss = derive(arrv, pm)
print('复核: 指针命中 %d/%d  未命中=%s' % (len(slot), Nv, miss))
# 桶表与实际分组
g = [slot[k] & 127 for k in range(Nv)]
i = 0; badb = 0
while i < Nv:
    gid = g[i]; j = i
    while j < Nv and g[j] == gid:
        j += 1
    k = gid
    if bv[k][0] != j - i or bv[k][1] != A0v + i * 4:
        badb += 1
    i = j
print('复核: 桶表与实际分组不符的组数 =', badb)
# 译文字数统计
cnt_cn = sum(1 for h, t in entsv if any('一' <= c <= '鿿' for c in t))
print('复核: 含汉字条目 %d / %d' % (cnt_cn, Nv))
for h in [0x0E58435C, 0x2053731C, 0x3342D5FC, 0x383B734F]:
    d = dict(entsv)
    print('   %08X -> %s' % (h, d[h]))
