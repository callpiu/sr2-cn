# -*- coding: utf-8 -*-
# 方案 B 安全版: 把 static_CH 中已知乱码的字幕记录替换为 static_US 的英文原文
# 1) 只读验证目标 key 在 US 表中的内容
# 2) 重建 static_CH.le_strings 并替换 patch.vpp_pc
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK = os.path.join(G, "patch.vpp_pc")

# ---------- le_strings 解析与重建 ----------
def ls_parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    off = 12 + buckets * 8
    n = len(data)
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    records = []
    for p in ptrs:
        if p == 0 or p >= n - 4: continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= n:
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        records.append(((id1 << 16) | id2, slots))
    return magic, ver, buckets, count, records

def ls_rebuild(magic, ver, buckets, count, records):
    # 保留原 bucket 表不变（只更新指针）
    # 但 bucket 表本身对 hash→index 的映射不依赖偏移，只依赖 count，所以不变
    out = struct.pack("<I H H I", magic, ver, buckets, count)
    # bucket table placeholder (8*buckets bytes of zeros — 实际我们不需要 bucket 表的功能)
    # 但原文件有 bucket 表，我们保留原始 bucket 表字节；这里因为 records 没变，bucket 表也有效
    # 为了安全，我们直接把原 bucket 表原样复制（它在文件里的位置和内容与记录无关）
    # 但我们没有这个数据了... 所以让我们在解析时保存它
    raise NotImplementedError("need to preserve bucket table")

# 先只读验证
v = Vpp(PK)
e_ch = v.find("static_CH", "le_strings")
e_us = v.find("static_US", "le_strings")
d_ch = v.read(e_ch)
d_us = v.read(e_us)

magic, ver, buckets, count, rec_ch = ls_parse(d_ch)
print("static_CH: magic=%#x ver=%d buckets=%d count=%d records=%d" % (magic, ver, buckets, count, len(rec_ch)))

magic2, ver2, buckets2, count2, rec_us = ls_parse(d_us)
print("static_US: magic=%#x ver=%d buckets=%d count=%d records=%d" % (magic2, ver2, buckets2, count2, len(rec_us)))

# 目标 key
targets = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A]

# 加载汉化 charlist
LC = [int(x) for x in re.findall(rb'\d+', v.read(v.find("charlist_CH", "txt")))]

def dec(slots, off=0x20):
    return "".join(chr(LC[w-off]) if off <= w-off < len(LC) else '?' for w in slots)

print("\n=== 目标记录在 CH / US 中的内容 ===")
for h in targets:
    ch = next((s for rh,s in rec_ch if rh == h), None)
    us = next((s for rh,s in rec_us if rh == h), None)
    print("\n%08X:" % h)
    print("  CH slots=%d  %s" % (len(ch) if ch else -1, dec(ch) if ch else "NOT FOUND"))
    print("  US slots=%d  %s" % (len(us) if us else -1, dec(us) if us else "NOT FOUND"))
