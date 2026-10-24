# -*- coding: utf-8 -*-
"""DLC le_strings 重建器 v4 —— 结构最终定案

布局（us/ch 通用）：
  0x00 u32 magic 0xA84C7F73
  0x04 u32 unk   0x00800001
  0x08 u32 N     条目数 (982)
  0x0C .. 0x40C  128 x (count u32, addr u32)     桶表
        bucket[k].count @ 0x0C + k*8
        bucket[k].addr  @ 0x10 + k*8   (文件偏移，指向数组区)
  0x40C .. 0x40C+N*4   N x u32 指针   按 hash&127 分 128 组，组内按 hash 升序
  TEXT0 = 0x40C + N*4 = 0x1364
  TEXT0 .. EOF        记录 [hash u32 BE][UTF-16BE 文本][0x0000]

★ 重建要点：
    - 桶表 addr 是数组区内偏移，数组大小固定 → 桶表【完全不用改】
    - 头部 0..0x40C 【完全不用改】
    - 记录区顺序可自由排列；只需重建 0x40C 起的 N 个指针
"""
import struct

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
HDRSZ = 0x40C          # 头 + 桶表
BUCKETS = 128


def load(path):
    raw = open(path, 'rb').read()
    N = struct.unpack_from('<I', raw, 0x08)[0]
    A0 = HDRSZ
    TEXT0 = A0 + N * 4
    arr = [struct.unpack_from('<I', raw, A0 + i * 4)[0] for i in range(N)]
    buckets = [(struct.unpack_from('<I', raw, 0x0C + k * 8)[0],
                struct.unpack_from('<I', raw, 0x10 + k * 8)[0]) for k in range(BUCKETS)]
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
    assert o == len(raw), '解析未到尾 %d/%d  %s' % (o, len(raw), path)
    assert len(ents) == N, '条目数不符 %d vs %d' % (len(ents), N)
    return raw, N, A0, TEXT0, buckets, arr, ents


def ptr_map(ents, TEXT0):
    m, o = {}, TEXT0
    for h, t in ents:
        m[o] = h
        o += 4 + 2 * len(t) + 2
    return m


def derive(arr, pm):
    """数组下标 -> hash"""
    slot, miss = {}, []
    for k, a in enumerate(arr):
        if a in pm:
            slot[k] = pm[a]
        else:
            miss.append((k, hex(a)))
    return slot, miss


def build(raw, N, A0, buckets, arr, ents, new_text, order=None):
    """new_text: hash -> 新文本。order: 记录写入顺序（hash 列表），默认 ents 原顺序"""
    head = raw[:A0]

    if order is None:
        order = [h for h, _ in ents]
    body = bytearray()
    pos = {}
    for h in order:
        t = new_text.get(h)
        if t is None:
            t = dict(ents)[h]
        pos[h] = A0 + N * 4 + len(body)
        body += struct.pack('>I', h)
        body += t.encode('utf-16-be')
        body += b'\x00\x00'

    pm = ptr_map(ents, A0 + N * 4)
    slot, miss = derive(arr, pm)
    assert not miss, '有指针未命中: %s' % miss[:5]
    out_arr = b''.join(struct.pack('<I', pos[slot[k]]) for k in range(N))
    return bytes(head) + out_arr + bytes(body), len(miss)


if __name__ == '__main__':
    raw, N, A0, TEXT0, buckets, arr, ents = load(G + 'dlc_us.le_strings')
    print('N=%d  A0=0x%X  TEXT0=0x%X  文件长=%d' % (N, A0, TEXT0, len(raw)))
    pm = ptr_map(ents, TEXT0)
    slot, miss = derive(arr, pm)
    print('指针命中 %d/%d  未命中=%s' % (len(slot), N, miss))

    # 桶表与实际分组一致性
    g = [slot[k] & 127 for k in range(N)]
    bounds, i = [], 0
    while i < N:
        gid = g[i]; j = i
        while j < N and g[j] == gid:
            j += 1
        bounds.append((gid, i, j - i)); i = j
    bad = sum(1 for k, (gid, si, c) in enumerate(bounds)
              if buckets[k][0] != c or buckets[k][1] != A0 + si * 4)
    print('桶表(count,addr) 与 hash&127 分组不符的桶数:', bad)
    print('count 之和 =', sum(c for c, _ in buckets))

    # 组内是否按 hash 升序
    insort = all(all(slot[p] < slot[p + 1] for p in range(s, s + c - 1))
                 for _, s, c in bounds)
    print('组内按 hash 升序?', insort)

    # ★ 回环：用英文原文重建，应与原文件逐字节相同
    out, _ = build(raw, N, A0, buckets, arr, ents, {})
    print('回环 %d vs %d  完全相同: %s' % (len(out), len(raw), out == raw))
