# -*- coding: utf-8 -*-
"""static_CH 全表健康检查：确认当前表结构完好（没被错位重建搞坏）"""
import sys, struct, re
sys.path.insert(0, "F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp = S.Vpp(game + "patch.vpp_pc")
buf = vp.read(vp.find("charlist_CH", "txt"))
end = buf.find(b"//ENDOFFILE")
cl = [int(x) for x in re.findall(rb"\d+", buf[:end if end > 0 else len(buf)])]

ent = vp.find("static_CH", "le_strings")
d = bytes(vp.read(ent))
magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
print("magic=%#x ver=%d buckets=%d count=%d size=%d" % (magic, ver, buckets, count, len(d)))
assert magic == 0xA84C7F73

off_at = 12 + buckets * 8
offs = [struct.unpack_from("<I", d, off_at + k * 4)[0] for k in range(count)]

bad_term = 0; bad_range = 0; empty = 0; dup_hash = {}
samples = []
for i, off in enumerate(offs):
    if off + 4 > len(d):
        bad_range += 1; continue
    id1, id2 = struct.unpack_from("<HH", d, off)
    h = (id1 << 16) | id2
    dup_hash[h] = dup_hash.get(h, 0) + 1
    p = off + 4; n = 0
    while True:
        if p + 1 >= len(d):
            bad_term += 1; break
        s = struct.unpack_from(">H", d, p)[0]
        if s == 0: break
        p += 2; n += 1
        if n > 400: bad_term += 1; break
    if n == 0: empty += 1
    if i % 1500 == 0:
        sl = [struct.unpack_from(">H", d, off + 4 + 2 * k)[0] for k in range(min(n, 28))]
        txt = "".join(chr(s) if 0x20 <= s <= 0x7E else (chr(cl[s - 0x20]) if 0 <= s - 0x20 < len(cl) else "?") for s in sl)
        samples.append((h, txt))

print("指针越界: %d | 缺终止符: %d | 空记录: %d" % (bad_range, bad_term, empty))
print("重复 hash 数: %d" % sum(1 for v in dup_hash.values() if v > 1))
print("\n抽样解码（每 1500 条取 1）:")
for h, t in samples:
    print("  %#010x  %s" % (h, t[:60]))
ok = (bad_range == 0 and bad_term == 0 and empty == 0)
print("\n结论:", "★ 表结构完好" if ok else "⚠ 表已损坏，必须还原")
