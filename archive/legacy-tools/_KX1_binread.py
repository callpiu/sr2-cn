# -*- coding: utf-8 -*-
# 假设：引擎把 charlist_CH.txt 当二进制 u16 数组读 -> 垃圾表 -> 二分查找返回插入位置 -> 碰撞
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
E = {"你": 331, "的": 1779, "弟": 405, "兄": 962, "们": 357, "需": 2651, "要": 2263,
     "保": 349, "护": 2337, "去": 530, "他": 296, "击": 1216, "谈": 2486, "几": 2229,
     "笔": 282, "生": 1287, "免": 538, "遭": 453, "袭": 1238}

f = Font(CN)
raw = f.v.read(f.cl_entry)
print("charlist_CH.txt 原始大小 = %d 字节" % len(raw))
print("前 64 字节:", raw[:64])
print()


def bsearch_exact(arr, key, signed=False):
    """标准二分：返回 (found_idx, lo, hi)  —— lo 是最终插入位置"""
    lo, hi = 0, len(arr) - 1
    k = (key - 0x10000 if key >= 0x8000 else key) if signed else key
    while lo <= hi:
        mid = (lo + hi) // 2
        v = arr[mid]
        if signed:
            v = v - 0x10000 if v >= 0x8000 else v
        if v == k:
            return mid, lo, hi
        if v < k:
            lo = mid + 1
        else:
            hi = mid - 1
    return None, lo, hi


def test(tag, arr, mode="lo", signed=False):
    hit = 0
    det = []
    for ch, want in E.items():
        got_i, lo, hi = bsearch_exact(arr, ord(ch), signed)
        got = got_i if got_i is not None else lo
        if mode == "foundonly":
            got = got_i
        if got == want:
            hit += 1
        if len(det) < 6:
            det.append("%s:%s/%s" % (ch, got, want))
    print("%-44s 命中=%2d/%d  %s" % (tag, hit, len(E), " ".join(det)))


# 各种「把文本当二进制」的解释
n_le = len(raw) // 2
A_le = list(struct.unpack_from("<%dH" % n_le, raw, 0))
A_be = list(struct.unpack_from(">%dH" % n_le, raw, 0))
print("u16 数组长度 = %d（文件 %d 字节）" % (n_le, len(raw)))
print()

test("u16LE 原始顺序 + 二分(取插入位置)", A_le)
test("u16BE 原始顺序 + 二分(取插入位置)", A_be)
test("u16LE 原始顺序 + 二分(仅精确命中)", A_le, "foundonly")
test("u16LE 排序后 + 二分(取插入位置)", sorted(A_le))
test("u16BE 排序后 + 二分(取插入位置)", sorted(A_be))
test("u16LE 原始顺序 + 有符号二分", A_le, "lo", True)
test("u16BE 原始顺序 + 有符号二分", A_be, "lo", True)

# 文本解析出的码点表（已知无效，做对照）
test("文本解析码点 + 二分", f.charlist)

# 另一个想法：引擎按「固定宽度记录」读文本（例如每 8 字节一条）
for w in (4, 6, 8, 10):
    n = len(raw) // w
    arr = []
    for i in range(n):
        chunk = raw[i * w:(i + 1) * w]
        arr.append(struct.unpack_from("<H", chunk, 0)[0])
    test("按 %d 字节/条 取首 u16 + 二分" % w, arr)
