import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"; W = r"F:\sr2-cn"
# 原厂繁中：搜「三王」「丈王」的槽位序列
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
CPS0 = [int(l) for l in v0.read(v0.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
def seq0(s):
    out=b""
    for ch in s:
        if ord(ch) in CPS0: out += (CPS0.index(ord(ch))+0x20).to_bytes(2,"little")
    return out
print("=== 原厂 patch 里搜（槽位序列）===")
for w in ("三王","丈王","三合","三合會","三王帮","3 Kings","3Kings"):
    # 中文字符串用槽位序列，英文用 ascii
    if all(ord(c) < 0x100 for c in w):
        pat = w.encode()
    else:
        pat = seq0(w)
    if not pat: 
        print("  %-10s (无法构造)" % w); continue
    found = []
    for nm in ("static_CH","voice_script_CH","platform_pc_CH"):
        e = v0.find(nm,"le_strings")
        if not e: continue
        d = bytes(v0.read(e))
        if pat in d: found.append(nm)
    print("  %-10s %s" % (w, found if found else "未找到"))
print()
# 第三方：搜 ascii 英文
v3 = Vpp(os.path.join(G,"patch.vpp_pc"))
print("=== 第三方 patch 里搜英文 ===")
for w in (b"3 Kings", b"3Kings", b"Kings", b"Three Kings"):
    found = []
    for nm in ("static_CH","voice_script_CH","platform_pc_CH"):
        e = v3.find(nm,"le_strings")
        if not e: continue
        d = bytes(v3.read(e))
        if w in d: found.append(nm)
    print("  %-14s %s" % (w.decode(), found if found else "未找到"))
