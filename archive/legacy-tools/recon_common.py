# -*- coding: utf-8 -*-
"""磁盘侧搜索 slot->错误码点 转换表 + common vf3 结构侦查。

锚点（内存实证 + 屏幕乱码串双向核对）：
  idx 332(们)->0x4F4D位  359(保)->0x4F2A伪  371(你)->0x4EFB任  390(兄)->0x5DE7巧
  1003(弟)->0x5076偶  1158(护)->0x8BE5该  1804(的)->0x74A8璨
  2264(要)->0x8861衡  2635(需)->0x96C4雄
slot 版 = idx + 32。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PY_OUT = []

#  anchors: (idx, codepoint)  —— 表若按 idx 索引
ANCH_IDX = [(332, 0x4F4D), (359, 0x4F2A), (371, 0x4EFB), (390, 0x5DE7),
            (1003, 0x5076), (1158, 0x8BE5), (1804, 0x74A8), (2264, 0x8861), (2635, 0x96C4)]
#  slot 版
ANCH_SLOT = [(i + 32, c) for i, c in ANCH_IDX]


def scan_bin(buf, anchors, stride, endian):
    """在 buf 里找满足 anchors 相对位置的数组。返回命中位置列表。"""
    fmt = ("<" if endian == "LE" else ">") + ("H" if stride == 2 else "I")
    exp = [(a[0] * stride, struct.pack(fmt, a[1])) for a in anchors]
    f_off, f_b = exp[0]
    res, start = [], 0
    while True:
        p = buf.find(f_b, start)
        if p < 0:
            break
        start = p + 1
        ok = True
        for off, b in exp[1:]:
            if buf[p + off:p + off + len(b)] != b:
                ok = False
                break
        if ok:
            res.append(p)
            if len(res) >= 20:
                break
    return res


def scan_lines(text, anchors_idx, anchors_slot):
    """十进制码点文本表：按纯数字行计数。"""
    vals = []
    for ln in text.splitlines():
        ln = ln.strip()
        if ln.isdigit():
            vals.append(int(ln))
    hits = []
    for name, anch in (("idx", anchors_idx), ("slot", anchors_slot)):
        for base in range(0, min(len(vals) - 2700, 4000) if len(vals) > 2700 else 0):
            pass
    # 直接按绝对位置查（表可能从头就是码点）
    for name, anch in (("idx", anchors_idx), ("slot", anchors_slot)):
        mx = max(a[0] for a in anch)
        if len(vals) <= mx:
            continue
        if all(vals[i] == c for i, c in anch):
            hits.append((name, len(vals)))
    return hits, len(vals)


def search_file(path, label, chunked=False):
    found = []
    try:
        sz = os.path.getsize(path)
    except OSError:
        return found
    if chunked and sz > 200 * 1024 * 1024:
        CH = 64 * 1024 * 1024
        OV = 1 << 16
        with open(path, "rb") as f:
            base = 0
            prev = b""
            while True:
                blk = f.read(CH)
                if not blk:
                    break
                buf = prev + blk
                b0 = base - len(prev)
                for anch, aname in ((ANCH_IDX, "idx"), (ANCH_SLOT, "slot")):
                    for stride in (2, 4):
                        for en in ("LE", "BE"):
                            for p in scan_bin(buf, anch, stride, en):
                                found.append(("%s@0x%X" % (aname, b0 + p), stride, en))
                prev = buf[-OV:]
                base += len(blk)
    else:
        buf = open(path, "rb").read()
        for anch, aname in ((ANCH_IDX, "idx"), (ANCH_SLOT, "slot")):
            for stride in (2, 4):
                for en in ("LE", "BE"):
                    for p in scan_bin(buf, anch, stride, en):
                        found.append(("%s@0x%X" % (aname, p), stride, en))
        # 十进制文本表
        try:
            t = buf.decode("utf-8", "replace")
            h, n = scan_lines(t, ANCH_IDX, ANCH_SLOT)
            for name, cnt in h:
                found.append(("TXT-%s lines=%d" % (name, cnt), 0, ""))
        except Exception:
            pass
    if found:
        print("  ★ %s : %s" % (label, found[:8]))
    return found


# ---------------------------------------------------------------- 1. common vf3 结构
print("=== common.vpp_pc fnt_chinese.vf3_pc 结构 ===")
vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
ents = vpc.entries()
print("  common.vpp_pc 共 %d 条目" % len(ents))
from collections import Counter
print("  扩展名top:", Counter(e["ext"] for e in ents).most_common(12))
for e in ents:
    nm = (e["name"] + "." + e["ext"]).lower()
    if any(k in nm for k in ("chinese", "fnt_", "char")):
        print("   entry: %-34s size=%d" % (nm, e["size"]))

ec = vpc.find("fnt_chinese", "vf3_pc")
buf = bytes(vpc.read(ec))
N = struct.unpack_from("<I", buf, 8)[0]
rec_end = 0xD0 + N * 16
print("\n  vf3: %d 字节, count@8=%d, 记录区结束=0x%X, tail=%d 字节"
      % (len(buf), N, rec_end, len(buf) - rec_end))
print("  tail 前96字节:", buf[rec_end:rec_end + 96].hex(" "))
print("  tail 若=2*N*4(UV) 则余 %d 字节" % (len(buf) - rec_end - 8 * N))

# patch vf3 对照
print("\n=== patch.vpp_pc fnt_chinese.vf3_pc 对照 ===")
vpp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
ep = vpp.find("fnt_chinese", "vf3_pc")
if ep:
    bp = bytes(vpp.read(ep))
    Np = struct.unpack_from("<I", bp, 8)[0]
    rend = 0xD0 + Np * 16
    print("  patch vf3: %d 字节, count=%d, tail=%d, 2*N*4=%d, 余=%d"
          % (len(bp), Np, len(bp) - rend, 8 * Np, len(bp) - rend - 8 * Np))
    print("  patch tail 前96:", bp[rend:rend + 96].hex(" "))

# ---------------------------------------------------------------- 2. 锚点搜索
print("\n=== 锚点二进制/文本搜索（idx 与 slot 两种索引 × stride2/4 × LE/BE）===")
targets = []
for fn in ("SR2_pc.exe", "DFEngine.dll"):
    p = os.path.join(G, fn)
    if os.path.exists(p):
        targets.append((p, fn))
targets.append((os.path.join(G, "common.vpp_pc"), "common.vpp_pc"))
targets.append((os.path.join(G, "patch.vpp_pc"), "patch.vpp_pc"))
tp = os.path.join(G, "textures.vpp_pc")
if os.path.exists(tp):
    targets.append((tp, "textures.vpp_pc"))
# 其他松散文件
for f in sorted(os.listdir(G)):
    p = os.path.join(G, f)
    if os.path.isfile(p) and p not in [t[0] for t in targets] and os.path.getsize(p) < 300 * 1024 * 1024:
        targets.append((p, f))

hits_total = []
for p, lb in targets:
    h = search_file(p, lb, chunked=True)
    hits_total += [(lb,) + x for x in h]
print("\n合计命中: %d" % len(hits_total))
for h in hits_total[:20]:
    print("   ", h)
