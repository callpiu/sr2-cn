# -*- coding: utf-8 -*-
# 反推引擎字符表 E 的生成规律：E(c) = 某个排序下的名次？
import re, struct, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

P = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
f = Font(P)
CL = f.charlist
print("charlist_vanilla = %d 项" % len(CL))

# 原版实测的 E(c)（= J - 5，J 来自截图并经裁格子视觉验证）
E_TARGET = {"交": 282, "他": 296, "你": 331, "保": 349, "們": 357, "兄": 405, "免": 412,
            "到": 453, "去": 530, "受": 538, "弟": 962, "擊": 1216, "攻": 1238, "易": 1287,
            "正": 1453, "的": 1779, "要": 2263, "護": 2337, "進": 2486, "避": 2509, "需": 2651}


def try_order(tag, keyfn):
    try:
        L = sorted(CL, key=keyfn)
    except Exception as e:
        print("%-28s 排序失败: %s" % (tag, e))
        return
    hit = 0
    det = []
    for ch, want in E_TARGET.items():
        cp = ord(ch)
        try:
            got = L.index(cp)
        except ValueError:
            got = None
        if got == want:
            hit += 1
        if len(det) < 8:
            det.append("%s:%s/%s" % (ch, got, want))
    print("%-28s 命中=%2d/%d  %s" % (tag, hit, len(E_TARGET), " ".join(det)))


def gbk(cp):
    try:
        return chr(cp).encode("gbk")
    except Exception:
        return b"\xff\xff\xff"


def big5(cp):
    try:
        return chr(cp).encode("big5")
    except Exception:
        return b"\xff\xff\xff"


try_order("Unicode(原顺序)", lambda cp: cp)
try_order("GBK 字节序", gbk)
try_order("Big5 字节序", big5)


def gbk_last(cp):
    try:
        chr(cp).encode("gbk")
        return (0, chr(cp).encode("gbk"))
    except Exception:
        return (1, b"")


def big5_last(cp):
    try:
        chr(cp).encode("big5")
        return (0, chr(cp).encode("big5"))
    except Exception:
        return (1, b"")


try_order("GBK(不可编码排后)", gbk_last)
try_order("Big5(不可编码排后)", big5_last)

# 也看看「去掉不可编码字符」后是否匹配
for codec in ("gbk", "big5"):
    L = []
    for cp in CL:
        try:
            chr(cp).encode(codec)
            L.append(cp)
        except Exception:
            pass
    hit = 0
    det = []
    for ch, want in E_TARGET.items():
        cp = ord(ch)
        got = L.index(cp) if cp in L else None
        if got == want:
            hit += 1
        if len(det) < 8:
            det.append("%s:%s/%s" % (ch, got, want))
    print("%-28s 命中=%2d/%d (len=%d) %s" % ("去掉%s不可编码" % codec, hit, len(E_TARGET), len(L), " ".join(det)))
