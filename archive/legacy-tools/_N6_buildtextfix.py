# -*- coding: utf-8 -*-
"""生成「改文本」修复包 —— 零副作用方案（纯 sr2font 实现，无 numpy 依赖）。

原理
    已知映射 c -> d（c 是想要的字，d 是引擎会显示 c 的字形时用的输入字）
    把 le_strings 记录里的 c 的槽位换成 d 的槽位

le_strings 格式（文档 §2.4）
    @0  magic 0xA84C7F73
    @4  ver u16
    @6  buckets u16
    @8  count u32
    @12 bucket 表（buckets×8：count u32 + offset u32）
    @12+buckets*8  pointer 数组（count×u32 绝对偏移）
    记录 = [id1 LE u16][id2 LE u16] + 大端 u16 槽位流 + 0x0000
    ID 字节序陷阱：文件前 4 字节 = 目标 hash 的 4 字节两两 swap
      例：84F287ED -> 文件里是 F2 84 ED 87

用法
    python _N6_buildtextfix.py <vpp输入> <vpp输出> [出=某 意=某]
"""
import os
import re
import sys
import struct
import hashlib

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

OFFSET = 5

MAP = {
    "你": "任", "的": "璨", "弟": "偶", "兄": "巧", "们": "位",
    "需": "雄", "要": "衡", "保": "伪", "护": "该",
    "去": "勾", "他": "亡", "击": "拮", "谈": "远", "几": "藐",
    "笔": "乱", "生": "携", "免": "匪", "遭": "冰", "袭": "挺",
    "出": None, "意": None,
}

# 目标 hash（文档里的记录 ID）
TARGETS = (0x84F287ED, 0x10AF1E62)


def load_charlist(vpp_path):
    v = Vpp(vpp_path)
    raw = v.read(v.find("charlist_CH", "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


# ---------------------------------------------------------------- le_strings
def le_strings_header(d):
    magic, = struct.unpack_from("<I", d, 0)
    ver, buckets = struct.unpack_from("<HH", d, 4)
    count, = struct.unpack_from("<I", d, 8)
    return magic, ver, buckets, count


def le_strings_records(d):
    """返回 [(record_offset, id1, id2, slots...)]"""
    magic, ver, buckets, count = le_strings_header(d)
    assert magic == 0xA84C7F73, "magic 不匹配: 0x%08X" % magic
    # bucket 表在 @12，每项 8 字节
    bucket_off = 12
    ptr_off = bucket_off + buckets * 8
    out = []
    seen = set()
    for i in range(count):
        p, = struct.unpack_from("<I", d, ptr_off + i * 4)
        if p in seen or p + 10 > len(d):
            continue
        seen.add(p)
        id1, id2 = struct.unpack_from("<HH", d, p)
        # 槽位流：大端 u16，直到 0x0000
        slots = []
        q = p + 4
        while q + 2 <= len(d):
            s, = struct.unpack_from(">H", d, q)
            if s == 0:
                break
            slots.append(s)
            q += 2
        out.append((p, id1, id2, slots))
    return out, bucket_off, ptr_off, buckets, count


def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    extra = {}
    for a in sys.argv[3:]:
        if "=" in a:
            k, v = a.split("=", 1)
            extra[k] = v
    mp = dict(MAP)
    mp.update(extra)
    missing = [k for k, v in mp.items() if not v]

    cl = load_charlist(src)
    IDX = {cp: i for i, cp in enumerate(cl)}
    print("charlist: %d 项" % len(cl))
    print("已知映射: %d 条" % sum(1 for v in mp.values() if v))
    if missing:
        print("★ 缺映射: %s（这些字保持不变）" % "".join(missing))
    print()

    # 定位 static_CH
    v = Vpp(src)
    ent = v.find("static_CH", "le_strings")
    abs_off = v.abs_offset(ent)
    size = ent["size"]
    raw = bytearray(open(src, "rb").read())
    d = bytearray(raw[abs_off:abs_off + size])
    print("static_CH @0x%X, %d 字节" % (abs_off, size))

    magic, ver, buckets, count = le_strings_header(d)
    print("  magic=0x%08X ver=%d buckets=%d count=%d" % (magic, ver, buckets, count))
    recs, b_off, p_off, nb, nc = le_strings_records(d)
    print("  解析出 %d 条记录" % len(recs))
    print()

    changed = 0
    for (p, id1, id2, slots) in recs:
        h = (id1 << 16) | id2
        h_sw = ((id1 & 0xFF) << 8 | (id1 >> 8)) << 16 | ((id2 & 0xFF) << 8 | (id2 >> 8))
        if h not in TARGETS and h_sw not in TARGETS:
            continue
        chars = []
        for s in slots:
            j = s - 0x20
            chars.append(chr(cl[j]) if 0 <= j < len(cl) else "?")
        old_txt = "".join(chars)
        new_chars = []
        for ch in chars:
            r = mp.get(ch)
            new_chars.append(r if r else ch)
        new_txt = "".join(new_chars)
        print("  记录 hash=0x%08X @0x%X (%d 槽位)" % (h, p, len(slots)))
        print("    原: %s" % old_txt)
        print("    新: %s" % new_txt)
        # 写回
        nw = 0
        for j, ch in enumerate(new_chars):
            cp = ord(ch)
            if cp not in IDX:
                continue
            s = IDX[cp] + 0x20
            q = p + 4 + j * 2
            old, = struct.unpack_from(">H", d, q)
            if old != s:
                struct.pack_into(">H", d, q, s)
                nw += 1
        print("    改了 %d 个槽位" % nw)
        changed += 1

    raw[abs_off:abs_off + size] = d
    open(dst, "wb").write(bytes(raw))
    md5 = hashlib.md5(open(dst, "rb").read()).hexdigest()
    print()
    print("已输出 %s  (修改 %d 条记录)" % (dst, changed))
    print("  md5 = %s" % md5)
    print()
    print("部署（先完全退出游戏）:")
    print('  cp "%s" "G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"' % dst)


if __name__ == "__main__":
    main()
