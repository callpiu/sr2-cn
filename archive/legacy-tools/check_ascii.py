import os, hashlib, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
import struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CUR = os.path.join(G, "patch.vpp_pc")
BAK = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"
def info(p):
    if not os.path.exists(p): return "不存在"
    v = Vpp(p)
    vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
    w = struct.unpack_from("<h", vf3, 0xD0)[0]
    cps = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    return "%d 字节 MD5=%s  ASCII width=%d  charlist=%d" % (os.path.getsize(p), hashlib.md5(open(p,'rb').read()).hexdigest()[:12].upper(), w, len(cps))
print("当前游戏 patch.vpp_pc : %s" % info(CUR))
print("备份(汉化+我的修复)    : %s" % info(BAK))
print()
# 汉化版里 ASCII 字符是否在 charlist
v = Vpp(CUR)
cps = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("=== 简体字表里 ASCII 覆盖情况 ===")
missing = [chr(c) for c in range(0x20, 0x7f) if c not in cps]
print("  0x20..0x7E 共 95 个，缺失 %d 个: %s" % (len(missing), "".join(missing) if missing else "无"))
if missing:
    print("  缺失字符的码点: %s" % [hex(ord(c)) for c in missing])
