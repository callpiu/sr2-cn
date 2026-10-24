# -*- coding: utf-8 -*-
"""DLC le_strings 重建器 v3 —— 修正 off-by-4

关键修正：指针数组里存的是【记录起点 o】（hash 所在位置），不是文本起点 o+4。

布局：
  0x000..0x008  magic + unk
  0x008..0x408  128 桶表项 (array_address, count)
  0x408..0x1360 982 条 u32 指针（按 hash 排序，引擎二分查找）
  0x1360..0x1364 4 字节 MID（原样保留）
  0x1364..EOF   记录 [hash u32 BE][UTF-16BE 文本][0x0000]
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
            if u == 0:
                break
            cps.append(u)
        ents.append((h, ''.join(chr(c) for c in cps)))
    assert o == len(raw), '解析未到尾 %d/%d' % (o, len(raw))
    return raw, hdr, arr, mid, ents


def ptr_map(ents):
    """记录起点 -> (hash, 文本)"""
    m = {}
    o = TEXT0
    for h, t in ents:
        m[o] = (h, t)          # ★ 记录起点，不是 o+4
        o += 4 + 2 * len(t) + 2
    return m


def build(hdr, mid, arr, arr_slot, ents, new_text):
    """arr_slot: 数组下标 -> hash；new_text: hash -> 新文本"""
    body = bytearray()
    pos = {}
    for h, t in ents:
        nt = new_text.get(h, t)
        pos[h] = TEXT0 + len(body)      # ★ 记录起点
        body += struct.pack('>I', h)
        body += nt.encode('utf-16-be')
        body += b'\x00\x00'
    out_arr = []
    for k in range(ARRN):
        h = arr_slot.get(k)
        out_arr.append(pos[h] if h is not None else arr[k])
    return (bytes(hdr)
            + b''.join(struct.pack('<I', v) for v in out_arr)
            + bytes(mid)
            + bytes(body))


def derive_slot(ents, arr):
    """从原始 arr 推导 数组下标 -> hash"""
    m = ptr_map(ents)
    slot, miss = {}, []
    for k, a in enumerate(arr):
        if a in m:
            slot[k] = m[a][0]
        else:
            miss.append((k, hex(a)))
    return slot, miss


if __name__ == '__main__':
    raw, hdr, arr, mid, ents = load(G + 'dlc_us.le_strings')
    slot, miss = derive_slot(ents, arr)
    print('条目数', len(ents))
    print('未命中陈旧指针:', miss)
    print('数组覆盖条目数', len(set(slot.values())), '/', len(ents))
    # 校验：数组顺序是否严格按 hash 升序
    hs = [slot[k] for k in range(ARRN) if k in slot]
    print('数组按 hash 升序?', all(hs[i] < hs[i + 1] for i in range(len(hs) - 1)))
    # 桶表校验
    buckets = [(struct.unpack_from('<I', raw, 8 + i * 8)[0],
                struct.unpack_from('<I', raw, 8 + i * 8 + 4)[0]) for i in range(128)]
    print('桶 count 之和 =', sum(c for _, c in buckets))
    # 回环
    out = build(hdr, mid, arr, slot, ents, {})
    print('回环重建 %d vs 原 %d  完全相同: %s' % (len(out), len(raw), out == raw))
    if out != raw:
        for i in range(min(len(out), len(raw))):
            if out[i] != raw[i]:
                print('首个差异 @0x%X' % i)
                break
        else:
            print('仅长度不同')
