import sys, os, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def getstrings(p):
    v=Vpp(p); e=v.find("static_CH","le_strings")
    if e is None: return None
    return v.read(e)
a = getstrings(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
b = getstrings(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
print("原始 static_CH %d 字节, 当前 %d 字节" % (len(a), len(b)))
def head(b, n=400):
    print("  前%d字节 hex: %s" % (n, b[:n].hex()))
    try:
        t = b[:n].decode('utf-16-le', 'replace')
        print("  按UTF-16LE: %r" % t[:200])
    except Exception as e: print(e)
    print("  可打印ASCII片段: %r" % re.findall(rb'[ -~]{6,}', b[:n])[:6])
print("\n=== 原始 ==="); head(a)
print("\n=== 当前 ==="); head(b)
# 统计非 ASCII 字节
for tag,x in (("原始",a),("当前",b)):
    hi = sum(1 for c in x if c > 127)
    zeros = x.count(0)
    print("\n%s: 高位字节=%d(%.1f%%) 零字节=%d(%.1f%%)" % (tag, hi, 100*hi/len(x), zeros, 100*zeros/len(x)))
