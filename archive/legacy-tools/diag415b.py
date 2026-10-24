# -*- coding: utf-8 -*-
"""诊断 v415b：从已知目标字节位置反推记录区起点与指针表含义。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
N = len(cps)
slot_of = {}
for i, cp in enumerate(cps):
    slot_of.setdefault(cp, i + 0x20)
blob = vp.read(vp.find("static_CH"))
print("len(blob) =", len(blob))

def hd(b, o, n):
    for i in range(0, n, 16):
        print("  %08X  %s" % (o + i, " ".join("%02X" % x for x in b[o+i:o+i+16])))

print("\n[1] blob 头 64B:")
hd(blob, 0, 64)

TGT_REL = 0x17F32          # 目标 slot 序列起点（相对 blob）
REC     = TGT_REL - 4      # 假设 ID 占前 4 字节
print("\n[2] 目标周围 (0x%X .. 0x%X):" % (REC - 16, TGT_REL + 40))
hd(blob, REC - 16, 64)
print("  ID 4B =", " ".join("%02X" % x for x in blob[REC:REC+4]))
print("  视为 2×u16 LE =", struct.unpack_from("<HH", blob, REC))
print("  视为 u32 LE   = 0x%08X" % struct.unpack_from("<I", blob, REC)[0])
print("  视为 u32 BE   = 0x%08X" % struct.unpack_from(">I", blob, REC)[0])

# [3] 在指针区 [0xC90, 0xCC00) 里找 == REC 或相对值 的项
print("\n[3] 在 0xC90..0xCC00 找 u32 == %d(0x%X):" % (REC, REC))
found = []
for p in range(0xC90, 0xCC00, 4):
    v = struct.unpack_from("<I", blob, p)[0]
    if v == REC:
        found.append(p)
print("   绝对命中:", ["0x%X" % p for p in found] or "无")
for RA in (0xCBFC, 0xCBF8, 0xC90 + 12250 * 4, 0xCC00):
    rel = REC - RA
    hit = [p for p in range(0xC90, 0xCC00, 4)
           if struct.unpack_from("<I", blob, p)[0] == rel and rel >= 0]
    print("   RA=0x%X -> rel=%d 命中 %s" % (RA, rel, ["0x%X" % p for p in hit] or "无"))

# [4] 指针区统计
print("\n[4] 0xC90..0xCBF8 (12250 项) 统计:")
vals = [struct.unpack_from("<I", blob, 0xC90 + i * 4)[0] for i in range(12250)]
print("   min=%d max=%d  不同值=%d  0 的个数=%d  递增?=%s"
      % (min(vals), max(vals), len(set(vals)), vals.count(0),
         all(vals[i] <= vals[i+1] for i in range(len(vals)-1))))
print("   前 20:", vals[:20])

# [5] 0xCBFC 起那串 u32 是不是指针（继续往后看多久还保持"递增小正数"）
print("\n[5] 从 0xCBF8 起的 u32 序列（看指针区实际有多长）:")
seq = []
p = 0xCBF8
while p + 4 <= len(blob):
    v = struct.unpack_from("<I", blob, p)[0]
    seq.append((p, v))
    p += 4
    if len(seq) > 40:
        break
for p, v in seq[:24]:
    print("   %08X = %-8d (0x%X)" % (p, v, v))

# [6] 试着求指针区结束点：连续 u32 保持 <len(blob) 且大致递增，直到出现 slot 数据
print("\n[6] 探测指针区结束（从 0xC90 起，值须递增且 <len）:")
p = 0xC90
last = -1
endp = None
while p + 4 <= len(blob):
    v = struct.unpack_from("<I", blob, p)[0]
    if v < last or v >= len(blob):
        endp = p
        break
    last = v
    p += 4
print("   首个违例 @0x%X (值=%d, 上一个=%d)" % (endp, struct.unpack_from("<I", blob, endp)[0], last))
print("   若指针区 = [0xC90, 0x%X) 则项数 = %d" % (endp, (endp - 0xC90) // 4))

# [7] 用该指针区（相对 endp 起点）验证记录
if endp:
    RA = endp
    print("\n[7] 假设记录区起点 RA=0x%X，指针=相对值:" % RA)
    ok = 0
    bad = 0
    tgt_idx = None
    for i in range((endp - 0xC90) // 4):
        v = struct.unpack_from("<I", blob, 0xC90 + i * 4)[0]
        o = RA + v
        if o + 4 > len(blob):
            bad += 1
            continue
        if o == REC:
            tgt_idx = i
        ok += 1
    print("   可解析 %d 条，越界 %d" % (ok, bad))
    print("   目标 REC=0x%X 对应指针下标 = %s" % (REC, tgt_idx))
    if tgt_idx is None:
        # 也许指针是绝对值
        for i in range((endp - 0xC90) // 4):
            v = struct.unpack_from("<I", blob, 0xC90 + i * 4)[0]
            if v == REC:
                print("   绝对值命中下标 =", i)
                tgt_idx = i
                break
    # 打印几条样本
    for i in (0, 1, 2, 3):
        v = struct.unpack_from("<I", blob, 0xC90 + i * 4)[0]
        o = RA + v
        sl = []
        q = o
        while q + 2 <= len(blob):
            s = struct.unpack_from(">H", blob, q)[0]
            q += 2
            if s == 0:
                break
            sl.append(s)
        txt = "".join(chr(cps[s-0x20]) if 0 <= s-0x20 < N else ("\n" if s == 10 else "<%d>" % s)
                      for s in sl[2:])
        print("   [%d] off=0x%X ID=(%d,%d) %r" % (i, o, sl[1], sl[0], txt[:60]))
