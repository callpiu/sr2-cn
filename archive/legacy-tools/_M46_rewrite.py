# -*- coding: utf-8 -*-
# 改写两句字幕：避开取格异常的字。句2 变长 -> 需重写记录区并更新 pointer 数组
import sys, os, struct, shutil, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
BAK = r"F:/sr2-cn/_backup_TEXT/patch.vpp_pc.before_rewrite"
OUT = r"F:/sr2-cn/_FIX/patch_rewrite.vpp_pc"

# 新文本（纯汉字，去掉 [format] 标记）
NEW = {
    (0x84F2, 0x87ED): "弟兄们需支援快去帮忙吧",       # 原 41 槽位(含format) -> 11
    (0x10AF, 0x1E62): "弟兄们出去做几单生意免受攻击",  # 原 52 槽位(含format) -> 14
}

cn = Vpp(SRC)
f = Font(SRC)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

# 校验新文本全部字符可编码
for k, t in NEW.items():
    bad = [c for c in t if c not in bidx]
    if bad:
        raise SystemExit("无法编码: %s" % "".join(bad))
print("新文本全部可编码")

for name in ("static_CH",):
    e = cn.find(name, "le_strings")
    d = bytearray(cn.read(e))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = list(struct.unpack_from("<%dI" % count, d, 12 + buckets * 8))

    # 逐条重写（紧凑排列），更新 pointer
    changed = 0
    newptrs = []
    wp = 12 + buckets * 8 + count * 4   # 记录区起点
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            newptrs.append(p); continue
        id1, id2 = struct.unpack_from("<HH", d, p)
        q = p + 4
        sl = []
        while True:
            s, = struct.unpack_from(">H", d, q); q += 2
            if s == 0: break
            sl.append(s)
        old_txt = "".join(B[s - 32] if 0 <= s - 32 < len(B) else "{%d}" % s for s in sl)

        newptrs.append(wp)
        struct.pack_into("<HH", d, wp, id1, id2)
        wp += 4
        if (id1, id2) in NEW:
            for ch in NEW[(id1, id2)]:
                struct.pack_into(">H", d, wp, bidx[ch] + 32)
                wp += 2
            changed += 1
            print("  改写 [%04X.%04X]\n     原(%d槽): %s\n     新(%d槽): %s" % (
                id1, id2, len(sl), old_txt[:60], len(NEW[(id1, id2)]), NEW[(id1, id2)]))
        else:
            for s in sl:
                struct.pack_into(">H", d, wp, s)
                wp += 2
        struct.pack_into(">H", d, wp, 0)
        wp += 2

    # 写回 pointer 数组
    for i, np_ in enumerate(newptrs):
        struct.pack_into("<I", d, 12 + buckets * 8 + i * 4, np_)
    print("\n重写完成：%d 条记录，新记录区末尾 = %d（原 %d）" % (count, wp, len(d)))

    # 校验：重新解码全部记录
    errs = 0
    for i in range(count):
        p = newptrs[i]
        if p + 6 > wp: errs += 1; continue
        q = p + 4
        while q + 2 <= wp:
            s, = struct.unpack_from(">H", d, q); q += 2
            if s == 0: break
            if not (32 <= s < 32 + len(B)):
                errs += 1; break
    print("校验：越界槽位 %d 处" % errs)

    # 抽查两条目标
    for i in range(count):
        p = newptrs[i]
        id1, id2 = struct.unpack_from("<HH", d, p)
        if (id1, id2) in NEW:
            q = p + 4; out = []
            while True:
                s, = struct.unpack_from(">H", d, q); q += 2
                if s == 0: break
                out.append(B[s - 32])
            print("  抽查 [%04X.%04X] = %s" % (id1, id2, "".join(out)))

    # 写回 vpp
    raw = bytearray(open(SRC, "rb").read())
    off = cn.abs_offset(e)
    raw[off:off + len(d)] = d
    os.makedirs(os.path.dirname(BAK), exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if not os.path.exists(BAK):
        shutil.copy2(SRC, BAK)
        print("\n已备份 ->", BAK)
    open(OUT, "wb").write(bytes(raw))
    print("输出:", OUT, " md5=", hashlib.md5(bytes(raw)).hexdigest())
