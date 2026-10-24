# -*- coding: utf-8 -*-
# 对比原 static_CH 与重建文件的结构差异
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

# 读原文件
v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("static_CH", "le_strings")
orig = v.read(e)

# 读我的重建文件（从备份包里提取）
# backup 是完整 patch.vpp_pc，需要从中读 static_CH
v2 = Vpp(r"F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB")
orig2 = v2.read(v2.find("static_CH", "le_strings"))

# 读我上次写的 patch（从当前 patch 读，但已经回滚了，所以就是原文件）
# 让我从 _backup_B 提取我生成的 patch？不，backup 是改动前的。
# 我的生成文件还在 patch.vpp_pc 里吗？已经回滚了。
# 我需要从 vpp_backup 或找其它副本
import glob
for p in glob.glob(r"F:/sr2-cn/vpp_backup/*.vpp_pc") + glob.glob(r"F:/sr2-cn/_backup_*/*.vpp_pc"):
    try:
        vv = Vpp(p)
        e2 = vv.find("static_CH", "le_strings")
        if e2 and vv.read(e2) != orig2:
            print("找到不同版本:", p, os.path.getsize(p))
            bad = vv.read(e2)
            break
    except Exception as ex:
        pass
else:
    print("未找到不同版本的 static_CH")
    bad = None

if bad:
    print("原大小:", len(orig2), "坏大小:", len(bad))
    # 对比前 64 字节
    print("\n前 64 字节对比:")
    for i in range(0, 64, 16):
        o = orig2[i:i+16]; b = bad[i:i+16]
        print("  orig %08x  %s  |  bad %08x  %s  %s" % (
            i, " ".join("%02X"%x for x in o),
            i, " ".join("%02X"%x for x in b),
            "OK" if o==b else "DIFF"))
    
    # 解析 header
    m1, v1, b1, c1 = struct.unpack_from("<I H H I", orig2, 0)
    m2, v2, b2, c2 = struct.unpack_from("<I H H I", bad, 0)
    print("\nheader: orig magic=%#x ver=%d buckets=%d count=%d" % (m1, v1, b1, c1))
    print("        bad  magic=%#x ver=%d buckets=%d count=%d" % (m2, v2, b2, c2))
    
    # 对比 bucket table
    print("\nbucket table 前 10 项:")
    for i in range(10):
        o1 = struct.unpack_from("<II", orig2, 12+i*8)
        o2 = struct.unpack_from("<II", bad, 12+i*8)
        print("  [%d] orig=%s bad=%s %s" % (i, o1, o2, "OK" if o1==o2 else "DIFF"))
    
    # 对比 pointer array
    off = 12 + b1 * 8
    print("\npointer array 前 10 项:")
    for i in range(10):
        p1 = struct.unpack_from("<I", orig2, off+i*4)[0]
        p2 = struct.unpack_from("<I", bad, off+i*4)[0]
        print("  [%d] orig=%08x bad=%08x %s" % (i, p1, p2, "OK" if p1==p2 else "DIFF"))
    
    # 检查 pointer 是否都指向记录开始
    print("\npointer 有效性检查:")
    for i in range(min(20, c1)):
        p = struct.unpack_from("<I", bad, off+i*4)[0]
        if p < 0 or p >= len(bad) - 4:
            print("  [%d] bad pointer %08x out of range!" % (i, p))
        else:
            h = struct.unpack_from("<HH", bad, p)
            print("  [%d] -> %08x  id=%04x %04x" % (i, p, h[0], h[1]))
