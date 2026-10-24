# -*- coding: utf-8 -*-
"""综合扫描（第二轮）：一次回答 4 个问题

A. 中文 le_strings 是否已驻留内存？        -> 搜 REC1 的 slot BE 字节
B. 乱码结果串（真 Unicode LE）是否在内存？  -> 搜 "任璨偶巧位"
C. 内存里有几张 charlist 副本？各是正是错？ -> 搜 u16 LE 的 ASCII 递增序列 20 00 21 00 ...
D. 错误的 idx->Unicode 转换表在哪？        -> 9 组映射双锚点 + 全量校验（弟=1035 已修正）
"""
import sys, os, struct, re, time
sys.path.insert(0, "F:/sr2-cn/stub")
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)
lim = C.addr_limit(h)

OUT = r"F:/sr2-cn/_扫描结果"
os.makedirs(OUT, exist_ok=True)
ts = time.strftime("%Y%m%d_%H%M%S")
fp = open(os.path.join(OUT, "scan2_%s.txt" % ts), "w", encoding="utf-8")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    fp.write(s + "\n")
    fp.flush()


P("pid=%d  地址上限 0x%X  开始 %s" % (pid, lim, time.strftime("%H:%M:%S")))

# ---------------- 准备字表 ----------------
CL = C.load_charlist()
P("charlist_CH 载入 %d 项" % len(CL))
CP2 = {cp: i + 0x20 for i, cp in enumerate(CL)}
IDX = {c: i for i, c in enumerate(CL)}   # 码点 -> 索引
FORBID = frozenset(b"\x00\r\n")

# 9 组已知「索引 -> 屏幕上看到的错字」
PAIRS = [(332, 0x4F4D), (371, 0x4EFB), (391, 0x4F2A), (422, 0x5DE7),
         (1035, 0x5076), (1190, 0x8BE5), (1836, 0x743F),
         (2296, 0x8861), (2667, 0x96C4)]
P("校验映射: " + " ".join("%d->%s" % (i, chr(u)) for i, u in PAIRS))

# ---------------- 通用：全内存搜字节模式 ----------------
def scan_bytes(pat, label, max_hits=40, chunk=32 * 1024 * 1024):
    """pat: bytes 或 compiled regex。返回命中地址列表"""
    hits = []
    total = 0
    nreg = 0
    isre = isinstance(pat, re.Pattern)
    for base, size, prot in C.enum_regions(h, lim):
        nreg += 1
        off = 0
        while off < size:
            n = min(chunk, size - off)
            raw = C.read_mem(h, base + off, n)
            if not raw:
                break
            total += len(raw)
            if isre:
                it = (m.start() for m in pat.finditer(raw))
            else:
                it = (m.start() for m in re.finditer(re.escape(pat), raw))
            for st in it:
                hits.append(base + off + st)
                if len(hits) >= max_hits:
                    return hits, total, nreg
            off += n
    return hits, total, nreg


def show_ctx(addr, n=96):
    raw = C.read_mem(h, max(0, addr - 32), n)
    if not raw:
        return
    P("     上下文 0x%X:" % addr)
    for i in range(0, len(raw), 16):
        P("       %08X  %s  |%s|" % (
            max(0, addr - 32) + i,
            raw[i:i + 16].hex(" ").upper().ljust(47),
            "".join(chr(b) if 32 <= b < 127 else "." for b in raw[i:i + 16])))


# ================= A. 中文表是否驻留 =================
P("\n" + "=" * 72)
P("A. 中文 le_strings 是否驻留内存")
patA = C.slots_be("你的") + C.be("[f")
P("   模式 %s  (%s)" % (patA.hex(" ").upper(), patA))
hits, total, nreg = scan_bytes(patA, "A", max_hits=10)
P("   扫过 %d 区 / %.1f MB  命中 %d 处" % (nreg, total / 1048576.0, len(hits)))
for a in hits[:6]:
    show_ctx(a)

# ================= B. 乱码结果串 =================
P("\n" + "=" * 72)
P("B. 乱码结果串（真 UTF-16LE）是否在内存")
for s in ("任璨偶巧位", "任璨偶", "雄衡任璨"):
    patB = C.le(s)
    hits, _, _ = scan_bytes(patB, "B", max_hits=10)
    P("   「%s」 %s -> 命中 %d 处" % (s, patB.hex(" ").upper(), len(hits)))
    for a in hits[:5]:
        show_ctx(a, 64)

# ================= C. 所有 charlist 副本 =================
P("\n" + "=" * 72)
P("C. 内存里的 charlist 副本（u16 LE 的 32,33,34,35,36,37 递增序列）")
asc = b"".join(struct.pack("<H", v) for v in range(32, 40))
asc_be = b"".join(struct.pack(">H", v) for v in range(32, 40))
for tag, pat in (("LE", asc), ("BE", asc_be)):
    hits, _, _ = scan_bytes(pat, "C", max_hits=60)
    P("   [%s] 模式 %s -> %d 处" % (tag, pat.hex(" ").upper(), len(hits)))
    seen = set()
    for a in hits:
        # 表基址 = 命中位置 - 0*2（因为模式从 idx0 开始）
        cand = a
        if cand in seen:
            continue
        seen.add(cand)
        tbl = C.read_mem(h, cand, 2795 * 2 + 8)
        if not tbl:
            continue
        vals = [struct.unpack_from("<H" if tag == "LE" else ">H", tbl, i * 2)[0]
                for i in (332, 371, 391, 422, 1035, 1190, 1836, 2296, 2667)]
        got = "".join(chr(v) if 32 <= v < 0xFFFF else "?" for v in vals)
        bad = sum(1 for (i, u), v in zip(PAIRS, vals) if v == u)
        P("     0x%X  idx[332,371,391,422,1035,1190,1836,2296,2667] = %s  (错表命中 %d/9)"
          % (cand, got, bad))
        if bad >= 3:
            P("     ★★★ 疑似错误转换表！基址 0x%X" % cand)

# ================= D. 9 组映射双锚点搜索 =================
P("\n" + "=" * 72)
P("D. 直接搜错误的 idx->Unicode 转换表（stride 2 / 4）")
for stride in (2, 4):
    for (i0, u0), (i1, u1) in (((1035, 0x5076), (1836, 0x743F)),
                               ((332, 0x4F4D), (371, 0x4EFB)),
                               ((371, 0x4EFB), (2667, 0x96C4))):
        gap = (i1 - i0) * stride - 2
        if gap < 0:
            continue
        for endian in ("<", ">"):
            p0 = struct.pack(endian + "H", u0)
            p1 = struct.pack(endian + "H", u1)
            pat = re.compile(re.escape(p0) + b".{%d}" % gap + re.escape(p1), re.S)
            hits, _, _ = scan_bytes(pat, "D", max_hits=200)
            if not hits:
                continue
            P("   stride=%d 锚点 %d/%d [%s] -> 粗筛 %d 处，逐条校验中..." %
              (stride, i0, i1, endian, len(hits)))
            for a in hits:
                cand = a - i0 * stride
                if cand < 0x10000:
                    continue
                ok = 0
                detail = []
                for i, u in PAIRS:
                    raw = C.read_mem(h, cand + i * stride, 2)
                    if not raw:
                        break
                    v = struct.unpack_from(endian + "H", raw, 0)[0]
                    detail.append(chr(v) if 32 <= v else "?")
                    if v == u:
                        ok += 1
                if ok >= 5:
                    P("     ★ 表基址 0x%X  stride=%d [%s]  %d/9  %s" %
                      (cand, stride, endian, ok, "".join(detail)))

# ================= E. 字形重映射表 g =================
# 渲染管线最终字形索引: 332->362 371->336 422->967 1035->410 1836->1784
P("\n" + "=" * 72)
P("E. 搜字形重映射表 g（idx->最终字形cell，u16/u32）")
GM = [(332, 362), (371, 336), (422, 967), (1035, 410), (1836, 1784)]
for stride in (2, 4):
    for endian in ("<", ">"):
        (i0, v0), (i1, v1) = GM[0], GM[1]
        gap = (i1 - i0) * stride - stride
        if gap < 0:
            continue
        pat = re.compile(re.escape(struct.pack(endian + "H", v0)) +
                         b".{%d}" % gap + re.escape(struct.pack(endian + "H", v1)), re.S)
        hits, _, _ = scan_bytes(pat, "E", max_hits=100)
        if not hits:
            continue
        P("   stride=%d [%s] 粗筛 %d 处" % (stride, endian, len(hits)))
        for a, in [(x,) for x in hits]:
            cand = a - i0 * stride
            if cand < 0x10000:
                continue
            ok = 0
            vals = []
            for i, j in GM:
                raw = C.read_mem(h, cand + i * stride, 2)
                v = struct.unpack_from(endian + "H", raw, 0)[0] if raw else -1
                vals.append(v)
                if v == j:
                    ok += 1
            if ok >= 4:
                P("     ★ g表基址 0x%X stride=%d [%s] 验证%d/5 vals=%s" %
                  (cand, stride, endian, ok, vals))

P("\n" + "=" * 72)
P("扫描结束 %s" % time.strftime("%H:%M:%S"))
C.k32.CloseHandle(h)
fp.close()
