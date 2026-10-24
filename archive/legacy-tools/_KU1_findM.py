# -*- coding: utf-8 -*-
# 用 19 个精确 (字符 -> 引擎索引) 数据，检验各种候选 M 定义
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
VAN = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"

# 汉化版实测（显示字 -> E = charlist.index(显示字) - 5）
E_HANHUA = {"你": 331, "的": 1779, "弟": 405, "兄": 962, "们": 357, "需": 2651, "要": 2263,
            "保": 349, "护": 2337, "去": 530, "他": 296, "击": 1216, "谈": 2486, "几": 2229,
            "笔": 282, "生": 1287, "免": 538, "遭": 453, "袭": 1238}
# 原版实测
E_VANILLA = {"交": 282, "他": 296, "你": 331, "保": 349, "們": 357, "兄": 405, "免": 412,
             "到": 453, "去": 530, "受": 538, "弟": 962, "擊": 1216, "攻": 1238, "易": 1287,
             "正": 1453, "的": 1779, "要": 2263, "護": 2337, "進": 2486, "避": 2509, "需": 2651}

fc = Font(CN); CLC = fc.charlist
fv = Font(VAN); CLV = fv.charlist
print("charlist 汉化=%d 原版=%d" % (len(CLC), len(CLV)))

# vf3 记录（每 16 字节 4 个 u32）
N = fc.N
RECS = [struct.unpack_from("<4I", fc.vf3, 0xD0 + k * 16) for k in range(N)]


def test(tag, L, TARGET, CL):
    """L: 候选表（字符码点列表）；检查 L.index(c) == E(c)"""
    hit = 0
    det = []
    for ch, want in TARGET.items():
        cp = ord(ch)
        try:
            got = L.index(cp)
        except ValueError:
            got = None
        if got == want:
            hit += 1
        if len(det) < 6:
            det.append("%s:%s/%s" % (ch, got, want))
    print("%-38s 命中=%2d/%d  %s" % (tag, hit, len(TARGET), " ".join(det)))


print("\n=== 针对汉化版（19 个点）===")
test("汉化 charlist 原顺序", list(CLC), E_HANHUA, CLC)
test("原版 charlist 原顺序", list(CLV), E_HANHUA, CLC)

try:
    test("汉化 charlist 按 GBK 排序", sorted(CLC, key=lambda c: chr(c).encode("gbk")), E_HANHUA, CLC)
except Exception as e:
    print("GBK 排序失败", e)
try:
    test("汉化 charlist 按 Big5 排序", sorted(CLC, key=lambda c: chr(c).encode("big5")), E_HANHUA, CLC)
except Exception as e:
    print("Big5 排序失败", e)

U = sorted(set(CLC) | set(CLV))
test("汉化∪原版 排序", U, E_HANHUA, CLC)
I = sorted(set(CLC) & set(CLV))
test("汉化∩原版 排序", I, E_HANHUA, CLC)

# 按 vf3 记录字段排序（汉化版 vf3）
for fi, nm in enumerate(["spacing", "byteWidth", "offset", "kerning"]):
    order = sorted(range(N), key=lambda k: (RECS[k][fi], k))
    L = [CLC[k] for k in order]
    test("汉化 charlist 按 vf3.%s 排序" % nm, L, E_HANHUA, CLC)

print("\n=== 针对原版（21 个点）===")
test("原版 charlist 原顺序", list(CLV), E_VANILLA, CLV)
fvN = fv.N
RECV = [struct.unpack_from("<4I", fv.vf3, 0xD0 + k * 16) for k in range(fvN)]
for fi, nm in enumerate(["spacing", "byteWidth", "offset", "kerning"]):
    order = sorted(range(fvN), key=lambda k: (RECV[k][fi], k))
    L = [CLV[k] for k in order]
    test("原版 charlist 按 vf3.%s 排序" % nm, L, E_VANILLA, CLV)
