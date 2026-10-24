import sys
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

v = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc")
e = v.find("charlist_CH", "txt")
b = v.read(e)
print("charlist_CH.txt  size=%d" % len(b))
print("--- 前 480 字节 ---")
print(repr(b[:480]))
print("--- 结尾 120 字节 ---")
print(repr(b[-120:]))
print()
lines = b.split(b"\n")
print("总行数=%d" % len(lines))
for i, L in enumerate(lines[:10]):
    print("  行%d: %r" % (i, L[:70]))
print("  ...")
print("  含 count= 的行号:", [i for i, L in enumerate(lines) if b"count=" in L])
print("  行尾 CRLF 数=%d  LF 数=%d" % (b.count(b"\r\n"), b.count(b"\n")))
