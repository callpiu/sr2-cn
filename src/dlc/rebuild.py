# -*- coding: utf-8 -*-
"""DLC le_strings 重编码器：验证结构理解 + 生成汉化版

布局（dlc_us 实测）：
  0x000..0x408  头部(8B) + 128 个桶 (off,count)，共 1024B
  0x408..0x1360 982 条 u32 文本指针（指向每条记录的文本部分，即 hash 之后）
  0x1360..0x1364 4 字节未知字段
  0x1364..EOF    记录： [hash u32 BE][UTF-16BE 文本][0x0000]
"""
import struct

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
HDR = 0x408          # 头部+桶表大小
ARRN = 982           # 指针数组条数
MID = 4              # 数组与文本区之间的 4 字节
TEXT0 = HDR + ARRN * 4 + MID   # = 0x1364

def load(path):
    raw = open(path, 'rb').read()
    hdr = raw[:HDR]
    arr = [struct.unpack_from('<I', raw, HDR + i * 4)[0] for i in range(ARRN)]
    mid = raw[HDR + ARRN * 4: TEXT0]
    o = TEXT0
    ents = []            # 文件顺序：(hash, text)
    while o + 4 <= len(raw):
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= len(raw):
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        ents.append((h, ''.join(chr(c) for c in cps)))
    assert o == len(raw), '解析未到文件尾: %d vs %d' % (o, len(raw))
    return hdr, arr, mid, ents

def array_order(ents, arr):
    """按数组顺序列出条目（利用原文件的指针定位）"""
    byT = {}
    o = TEXT0
    for h, t in ents:
        byT[o + 4] = (h, t)
        o += 4 + 2 * len(t) + 2
    out = []
    for a in arr:
        if a not in byT:
            raise KeyError('指针 0x%X 未命中任何条目' % a)
        out.append(byT[a])
    return out

def build(hdr, mid, ordered_hashes, texts_by_hash, file_order_hashes):
    """ordered_hashes: 数组顺序的 hash 列表；file_order_hashes: 文本区写入顺序"""
    body = bytearray()
    pos = {}
    for h in file_order_hashes:
        t = texts_by_hash[h]
        pos[h] = TEXT0 + len(body) + 4
        body += struct.pack('>I', h)
        body += t.encode('utf-16-be')
        body += b'\x00\x00'
    arr = b''.join(struct.pack('<I', pos[h]) for h in ordered_hashes)
    return bytes(hdr) + arr + bytes(mid) + bytes(body)

if __name__ == '__main__':
    hdr, arr, mid, ents = load(G + 'dlc_us.le_strings')
    print('条目', len(ents), 'mid 字段', mid.hex())
    ordered = array_order(ents, arr)
    print('数组顺序条目数', len(ordered))
    texts = {h: t for h, t in ents}
    file_order = [h for h, t in ents]
    out = build(hdr, mid, [h for h, t in ordered], texts, file_order)
    src = open(G + 'dlc_us.le_strings', 'rb').read()
    print('回环重建 大小 %d vs 原 %d  字节完全相同: %s' % (len(out), len(src), out == src))
    if out != src:
        for i in range(min(len(out), len(src))):
            if out[i] != src[i]:
                print('首个差异 @0x%X  out=%02x src=%02x' % (i, out[i], src[i]))
                break
