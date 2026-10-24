# -*- coding: utf-8 -*-
"""第三轮扫描（用户已触发活动字幕）

核心目标：把「错误字表 T」整张 dump 出来。
已知（内存实测，100% 可靠）：
    错误表 T 满足  T[332]=位U+4F4D  T[371]=任U+4EFB  T[422]=巧U+5DE7
                  T[1035]=偶U+5076 T[1836]=璨U+74A8
    正确表 charlist_CH 里这些字的索引分别是 362 / 336 / 967 / 410 / 1784
    => T 是同一字集的另一种排列（g: 332->362 371->336 422->967 1035->410 1836->1784）
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
fp = open(os.path.join(OUT, "scan3_%s.txt" % ts), "w", encoding="utf-8")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    fp.write(s + "\n")
    fp.flush()


P("pid=%d  地址上限 0x%X  开始 %s" % (pid, lim, time.strftime("%H:%M:%S")))

CL = C.load_charlist()
C.CL = CL
P("charlist_CH 载入 %d 项  首=%s 末=%s"
  % (len(CL), "".join(chr(c) for c in CL[:6]), "".join(chr(c) for c in CL[-4:])))

# 内存实测可靠的 5 组：索引 -> 屏幕上真出现的 Unicode
P5 = [(332, 0x4F4D), (371, 0x4EFB), (422, 0x5DE7), (1035, 0x5076), (1836, 0x74A8)]
P("可靠映射: " + " ".join("%d->%s(U+%04X)" % (i, chr(u), u) for i, u in P5))
CP = set(CL)
P("这 5 个错字是否都在 charlist_CH 里: " +
  ", ".join("%s=%s" % (chr(u), (CL.index(u) if u in CP else "不在")) for _, u in P5))

# ---------------- 全内存扫描 ----------------
def scan_all(pat, max_hits=100000, chunk=32 * 1024 * 1024, quiet=False):
    hits, total, nreg = [], 0, 0
    isre = isinstance(pat, re.Pattern)
    if not isre:
        pat = re.compile(re.escape(pat))
    for base, size, prot in C.enum_regions(h, lim):
        nreg += 1
        off = 0
        while off < size:
            n = min(chunk, size - off)
            raw = C.read_mem(h, base + off, n)
            if not raw:
                break
            total += len(raw)
            for m in pat.finditer(raw):
                hits.append(base + off + m.start())
                if len(hits) >= max_hits:
                    return hits, total, nreg
            off += n
    return hits, total, nreg


def dump_tbl(addr, tag, endian, want=4096):
    """读一张 u16 表，判断长度，校验 5 点，落盘"""
    raw = C.read_mem(h, addr, want * 2)
    if not raw or len(raw) < 4000:
        return None
    fmt = endian + "H"
    n = len(raw) // 2
    vals = struct.unpack_from("<%dH" % n, raw, 0) if endian == "<" else struct.unpack_from(">%dH" % n, raw, 0)
    # 推断长度：从 idx0 起连续有效字符（32..0xFFFD，非 0）
    L = 0
    for i in range(n):
        v = vals[i]
        if v == 0 or v > 0xFFFD:
            break
        L += 1
    got = []
    ok = 0
    for i, u in P5:
        v = vals[i] if i < n else -1
        got.append(chr(v) if 32 <= v < 0xFFFE else "?")
        if v == u:
            ok += 1
    asc = sum(1 for i in range(min(95, L)) if vals[i] == 32 + i)
    P("   0x%X [%s] 推断长度=%d  连续ASCII=%d/95  5点=%s  命中%d/5%s"
      % (addr, endian, L, asc, "".join(got), ok, "   ★★★错误表★★★" if ok >= 4 else ""))
    if ok >= 2 or L > 2000:
        p = os.path.join(OUT, "tbl_%s_0x%X_%s.bin" % (tag, addr, endian))
        with open(p, "wb") as f:
            f.write(raw[:max(L, 2000) * 2])
        P("      -> 已落盘 %s" % os.path.basename(p))
    return vals[:L] if L else None


# ================= A. 中文 le_strings 是否驻留 =================
P("\n" + "=" * 72)
P("A. 中文 le_strings slot 流是否驻留")
patA = C.slots_be("你的") + C.be("[f")
hits, total, nreg = scan_all(patA, max_hits=10)
P("   模式 %s -> %d 处 (%.1fMB / %d 区)"
  % (patA.hex(" ").upper(), len(hits), total / 1048576.0, nreg))
for a in hits[:5]:
    raw = C.read_mem(h, a - 48, 128)
    if raw:
        for i in range(0, len(raw), 16):
            P("     %08X  %s" % (a - 48 + i, raw[i:i + 16].hex(" ").upper()))

# ================= B. 乱码结果串 =================
P("\n" + "=" * 72)
P("B. 乱码结果串（长度前缀 + 真 UTF-16LE）")
for s in ("任璨偶巧位", "你的弟兄们", "你的", "弟兄们"):
    patB = C.le(s)
    hits, _, _ = scan_all(patB, max_hits=20)
    P("   「%s」 -> %d 处" % (s, len(hits)))
    for a in hits[:4]:
        raw = C.read_mem(h, a - 24, 96)
        if raw:
            P("     0x%X  %s" % (a, raw.hex(" ").upper()))

# ================= C. 所有 charlist 副本（核心） =================
P("\n" + "=" * 72)
P("C. 全内存搜索字表副本（u16 递增 ASCII 前缀），并整表 dump")
for endian in ("<", ">"):
    asc = b"".join(struct.pack(endian + "H", v) for v in range(32, 40))
    hits, _, _ = scan_all(asc, max_hits=200000)
    P("   [%s] 模式 %s -> %d 处，逐条读取..." % (endian, asc.hex(" ").upper(), len(hits)))
    seen = set()
    found = 0
    for a in hits:
        if a in seen:
            continue
        seen.add(a)
        # 表内 idx0..7 = 32..39，所以命中地址即表基址
        tbl = dump_tbl(a, "C", endian)
        if tbl:
            found += 1
    P("   [%s] 有效表 %d 张" % (endian, found))

# ================= D. 双锚点搜错误表（不要求前导 ASCII） =================
P("\n" + "=" * 72)
P("D. 双锚点搜索（stride 2/4，大小端），允许表头不是 ASCII")
combos = [(332, 371), (332, 422), (371, 422), (332, 1035), (1035, 1836), (422, 1836)]
P5D = dict(P5)
for stride in (2, 4):
    for i0, i1 in combos:
        u0, u1 = P5D[i0], P5D[i1]
        gap = (i1 - i0) * stride - stride
        if gap < 0:
            continue
        for endian in ("<", ">"):
            if stride == 4:
                # u32 存储，高 16 位未知 -> 用 2 字节锚点+间隔即可（低16位对齐）
                pat = re.compile(re.escape(struct.pack(endian + "H", u0)) +
                                 b".{%d}" % gap +
                                 re.escape(struct.pack(endian + "H", u1)), re.S)
            else:
                pat = re.compile(re.escape(struct.pack(endian + "H", u0)) +
                                 b".{%d}" % gap +
                                 re.escape(struct.pack(endian + "H", u1)), re.S)
            hits, _, _ = scan_all(pat, max_hits=20000)
            if not hits:
                continue
            P("   stride=%d 锚点 %d/%d [%s] 粗筛 %d 处" % (stride, i0, i1, endian, len(hits)))
            for a in hits[:200]:
                cand = a - i0 * stride
                if cand < 0x10000:
                    continue
                ok = 0
                det = []
                for i, u in P5:
                    r = C.read_mem(h, cand + i * stride, 2)
                    if not r:
                        break
                    v = struct.unpack_from(endian + "H", r, 0)[0]
                    det.append(chr(v) if 32 <= v < 0xFFFE else "?")
                    if v == u:
                        ok += 1
                if ok >= 4:
                    P("     ★ 表基址 0x%X stride=%d [%s] %d/5 %s" % (cand, stride, endian, ok, "".join(det)))
                    dump_tbl(cand, "D", endian)

# ================= E. 字形重映射表 g =================
P("\n" + "=" * 72)
P("E. 搜字形重映射表 g（i -> 正确表索引，值 362/336/967/410/1784）")
GM = [(332, 362), (371, 336), (422, 967), (1035, 410), (1836, 1784)]
for stride in (2, 4):
    for endian in ("<", ">"):
        (i0, v0), (i1, v1) = GM[0], GM[1]
        gap = (i1 - i0) * stride - stride
        pat = re.compile(re.escape(struct.pack(endian + "H", v0)) +
                         b".{%d}" % gap + re.escape(struct.pack(endian + "H", v1)), re.S)
        hits, _, _ = scan_all(pat, max_hits=20000)
        if not hits:
            continue
        P("   stride=%d [%s] 粗筛 %d 处" % (stride, endian, len(hits)))
        for a in hits[:200]:
            cand = a - i0 * stride
            if cand < 0x10000:
                continue
            ok = 0
            vs = []
            for i, j in GM:
                r = C.read_mem(h, cand + i * stride, 2)
                v = struct.unpack_from(endian + "H", r, 0)[0] if r else -1
                vs.append(v)
                if v == j:
                    ok += 1
            if ok >= 4:
                P("     ★ g表 0x%X stride=%d [%s] %d/5 vals=%s" % (cand, stride, endian, ok, vs))

P("\n" + "=" * 72)
P("扫描结束 %s" % time.strftime("%H:%M:%S"))
C.k32.CloseHandle(h)
fp.close()
