# -*- coding: utf-8 -*-
# 验证：common.vpp_pc 里的 fnt_chinese.vf3_pc 官方版 vs 汉化版
import sys, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

FILES = [
    ("官方原版 common（你之前装的）", r"F:/sr2-cn/_backup_CN/common.vpp_pc.official_20261017_0402"),
    ("汉化版 common（刚装上）",       r"G:/SteamLibrary/steamapps/common/Saints Row 2/common.vpp_pc"),
    ("patch.vpp_pc 里的表（对照）",   r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"),
]

for tag, path in FILES:
    try:
        v = Vpp(path)
    except Exception as e:
        print("[%s] 打不开: %s" % (tag, e))
        continue
    e = v.find("fnt_chinese", "vf3_pc")
    if not e:
        print("[%s] 没有 fnt_chinese.vf3_pc" % tag)
        continue
    b = v.read(e)
    N = struct.unpack_from("<I", b, 8)[0]
    UOFF = 0xD0 + N * 16
    VOFF = UOFF + N * 4
    U = [struct.unpack_from("<i", b, UOFF + k * 4)[0] for k in range(min(N, (len(b) - UOFF) // 4))]
    uniq = sorted(set(U))
    gaps = sorted(set(uniq[i + 1] - uniq[i] for i in range(len(uniq) - 1)))
    print("\n[%s]" % tag)
    print("   size=%d  md5=%s" % (len(b), hashlib.md5(b).hexdigest()))
    print("   N=%d   U 唯一值个数=%d   U 间隔集合=%s" % (N, len(uniq), gaps[:8]))
    print("   U 前 12 个 = %s" % U[:12])
    if gaps == [31]:
        print("   ⇒ **U 是图集列坐标（间隔恒为 31）**")
    else:
        print("   ⇒ U 不是图集坐标（间隔杂乱，疑似字距/kerning）")
