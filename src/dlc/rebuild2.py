# -*- coding: utf-8 -*-
"""DLC le_strings 重建器（带 2 个“陈旧指针”保护）

布局：
  0x000..0x408  头部8B + 122? 桶表（整体原样保留）
  0x408..0x1360 982 条 u32 文本指针（数组顺序 = 按 hash 排序，引擎二分查找）
  0x1360..0x1364 4 字节（原样保留）
  0x1364..EOF   记录 [hash u32 BE][UTF-16BE][0x0000]（写入顺序 = 原文件顺序）
"""
import struct

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
HDR = 0x408
ARRN = 982
TEXT0 = 0x1364

def load(path):
    raw = open(path, 'rb').read()
    hdr = raw[:HDR]
    arr = [struct.unpack_from('<I', raw, HDR + i * 4)[0] for i in range(ARRN)]
    mid = raw[HDR + ARRN * 4: TEXT0]
    o = TEXT0
    ents = []
    while o + 4 <= len(raw):
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= len(raw):
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        ents.append((h, ''.join(chr(c) for c in cps)))
    assert o == len(raw), '解析未到尾 %d/%d' % (o, len(raw))
    return raw, hdr, arr, mid, ents

def ptr_map(ents):
    """文本指针 -> (hash, 文本)"""
    m = {}
    o = TEXT0
    for h, t in ents:
        m[o + 4] = (h, t)
        o += 4 + 2 * len(t) + 2
    return m

def build(hdr, mid, arr, arr_slot_entry, ents, new_text):
    """arr_slot_entry: 数组下标 -> hash（None 表示保留原值）"""
    body = bytearray()
    pos = {}
    for h, t in ents:
        nt = new_text.get(h, t)
        pos[h] = TEXT0 + len(body) + 4
        body += struct.pack('>I', h)
        body += nt.encode('utf-16-be')
        body += b'\x00\x00'
    out_arr = []
    for k in range(ARRN):
        h = arr_slot_entry.get(k)
        out_arr.append(pos[h] if h is not None else arr[k])
    return bytes(hdr) + b''.join(struct.pack('<I', v) for v in out_arr) + bytes(mid) + bytes(body)

if __name__ == '__main__':
    raw, hdr, arr, mid, ents = load(G + 'dlc_us.le_strings')
    m = ptr_map(ents)
    slot = {}
    bogus = []
    for k, a in enumerate(arr):
        if a in m:
            slot[k] = m[a][0]
        else:
            bogus.append((k, hex(a)))
    print('条目数', len(ents), ' 陈旧指针(原样保留):', bogus)
    print('数组覆盖条目数', len(set(slot.values())), '/', len(ents))
    out = build(hdr, mid, arr, slot, ents, {})
    print('回环重建 %d vs 原 %d  完全相同: %s' % (len(out), len(raw), out == raw))
    if out != raw:
        for i in range(min(len(out), len(raw))):
            if out[i] != raw[i]:
                print('首个差异 @0x%X' % i); break
        else:
            print('长度不同')
    # 现有汉化版是否与英文 hash 对齐（抽样）
    raw2, hdr2, arr2, mid2, ents2 = load(G + 'dlc_ch.le_strings')
    d_en = dict(ents); d_cn = dict(ents2)
    import random
    random.seed(7)
    sample = [h for h, t in ents if any('一' <= c <= '鿿' for c in d_cn.get(h, ''))]
    for h in random.sample(sample, min(18, len(sample))):
        print('\nEN: %r\nCN: %r' % (d_en[h][:88], d_cn[h][:88]))
