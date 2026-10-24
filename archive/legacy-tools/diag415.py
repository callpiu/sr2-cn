# -*- coding: utf-8 -*-
"""诊断 v415：static_CH 的真正布局 —— 用偏移表精确定位记录，而非扫描。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")

vp = sr2lib.Vpp(SRC)
cps = [int(l) for l in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
N = len(cps)
slot_of = {}
for i, cp in enumerate(cps):
    slot_of.setdefault(cp, i + 0x20)

ent = vp.find("static_CH")
base = vp.data_start + ent["body"]
blob = vp.read(ent)
print("static_CH: body=%d size=%d  文件绝对起点=0x%X  len=%d"
      % (ent["body"], ent["size"], base, len(blob)))

h = struct.unpack_from("<8I", blob, 0)
print("头 8 个 u32:", h)
N_ENT, N_BUK = h[2], h[3]
TS = 16 + N_BUK * 8 + N_ENT * 4 + 4
print("N_ENT=%d N_BUK=%d TS=0x%X" % (N_ENT, N_BUK, TS))

# --- 桶表 ---
print("\n桶表前 6 项 @0x10:")
for k in range(6):
    a, b = struct.unpack_from("<II", blob, 16 + k * 8)
    print("  bucket[%d] = (%d, 0x%X)" % (k, a, b))

# --- 偏移表 ---
OA = 16 + N_BUK * 8
print("\n偏移表 @0x%X 前 8 项:" % OA)
for i in range(8):
    print("  [%d] = %d (0x%X)" % (i, struct.unpack_from("<I", blob, OA + i * 4)[0],
                                  struct.unpack_from("<I", blob, OA + i * 4)[0]))
print("末尾 4 字节 @0x%X = %d" % (OA + N_ENT * 4,
      struct.unpack_from("<I", blob, OA + N_ENT * 4)[0]))

# --- 文本区头部 hexdump ---
print("\n文本区起点 0x%X hexdump 64B:" % TS)
row = blob[TS:TS + 64]
print("  " + " ".join("%02X" % b for b in row[:32]))
print("  " + " ".join("%02X" % b for b in row[32:64]))


def dec(sl):
    return "".join(chr(cps[s - 0x20]) if 0 <= s - 0x20 < N
                   else ("\n" if s == 10 else "<%d>" % s) for s in sl)


def read_rec(b, o):
    """从 o 读一条：4B ID(2×u16 LE) + slots(BE u16) 至 0x0000"""
    sl = []
    p = o
    while True:
        s = struct.unpack_from(">H", b, p)[0]
        p += 2
        if s == 0:
            break
        sl.append(s)
    return sl, p


# 假设1：偏移表是绝对 blob 偏移
print("\n=== 假设1：偏移表值 = 绝对 blob 偏移 ===")
v0 = struct.unpack_from("<I", blob, OA)[0]
print("  表[0]=%d  TS=%d  len=%d" % (v0, TS, len(blob)))
if TS <= v0 < len(blob):
    sl, p = read_rec(blob, v0)
    print("  读 [%d]: ID=(%d,%d) 文本=%r  下一条@%d" % (v0, sl[1], sl[0], dec(sl[2:]), p))
    sl2, p2 = read_rec(blob, p)
    print("  下一条: ID=(%d,%d) 文本=%r" % (sl2[1], sl2[0], dec(sl2[2:])))

# 假设2：偏移表值 = 相对 TS
print("\n=== 假设2：偏移表值 = 相对 TS ===")
if 0 <= v0 < len(blob) - TS:
    sl, p = read_rec(blob, TS + v0)
    print("  读 TS+%d: ID=(%d,%d) 文本=%r" % (v0, sl[1], sl[0], dec(sl[2:])))

# --- 用偏移表全量解析，找目标 ---
target = "斯蒂尔沃特大学学生会"
tgt_slots = [slot_of[ord(c)] for c in target]
print("\n目标 slots =", tgt_slots)
tgt_bytes = b"".join(struct.pack(">H", s) for s in tgt_slots)

# 全盘搜字节
hits = []
off = 0
while True:
    i = blob.find(tgt_bytes, off)
    if i < 0:
        break
    hits.append(i)
    off = i + 1
print("blob 内命中偏移(相对) =", ["0x%X" % h for h in hits],
      "文件绝对 =", ["0x%X" % (h + base) for h in hits])

# 用偏移表逐条解析所有记录
recs = []
for i in range(N_ENT):
    v = struct.unpack_from("<I", blob, OA + i * 4)[0]
    recs.append((i, v))
print("\n偏移表值范围: min=%d max=%d (TS=%d, len=%d)"
      % (min(v for _, v in recs), max(v for _, v in recs), TS, len(blob)))

for base_guess, label in ((0, "绝对"), (TS, "相对TS")):
    byid = {}
    ok = 0
    for i, v in recs:
        o = v + base_guess
        if not (TS <= o < len(blob) - 4):
            continue
        sl, _ = read_rec(blob, o)
        if len(sl) >= 2:
            byid.setdefault((sl[1], sl[0]), (o, sl))
            ok += 1
    print("\n[%s] 可解析 %d/%d 条；ID=(3205,14500) %s"
          % (label, ok, N_ENT,
             "命中 " + repr(dec(byid[(3205, 14500)][1][2:])) if (3205, 14500) in byid else "未命中"))
    if (3205, 14500) in byid:
        o, sl = byid[(3205, 14500)]
        print("    记录起点 0x%X  文本=%r  slots=%s" % (o, dec(sl[2:]), sl[2:]))
