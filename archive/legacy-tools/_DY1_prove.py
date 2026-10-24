import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); e = v.find("charlist_CH","txt")
    t = v.read(e).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
nums_O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
nums_M = cl(os.path.join(G,"patch.vpp_pc"))
print("official table %d entries, mine %d entries" % (len(nums_O), len(nums_M)))
SENT = "your brothers need your protection"
cp = [ord(c) for c in SENT]
print("sentence:", SENT)
print("codepoints:", [hex(x) for x in cp])
print("my-table index:", [nums_M.index(x) for x in cp])
wrong = [336,1784,410,967,362,2656,2268,354,2342]
print("\n* characters at wrong indices in OFFICIAL table:")
for w in wrong:
    v = nums_O[w] if w < len(nums_O) else None
    print("   idx %4d -> U+%04X %s" % (w, v, chr(v) if v and 32<=v<0x30000 else '?'))
