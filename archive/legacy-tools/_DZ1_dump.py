import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p,name="static_CH",ext="le_strings"):
    v=Vpp(p); return v.read(v.find(name,ext))
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
nums_M = cl(os.path.join(G,"patch.vpp_pc"))
def dec(x, nums, skip):
    txt = x[skip:]
    m = len(txt)//2
    codes = struct.unpack_from("<%dH"%m, txt, 0)
    out=[]
    for c in codes:
        if c == 0: out.append("\n")
        elif c < 32: out.append("")
        elif c-32 < len(nums): out.append(chr(nums[c-32]))
        else: out.append("{%d}"%c)
    return "".join(out)
x = get(os.path.join(G,"patch.vpp_pc"))
n = struct.unpack_from('<I', x, 8)[0]
dirstart = 12; dirend = dirstart + n*8
print("static_CH: %d bytes, n=%d, dirend=%d, skip=%d" % (len(x), n, dirend, dirend+1))
t = dec(x, nums_M, dirend+1)
# find CJK-rich lines
lines = [l for l in t.split("\n")]
cjk = [ (i,l) for i,l in enumerate(lines) if sum(1 for ch in l if 0x4E00<=ord(ch)<0x9FFF) >= 4 ]
print("total lines %d, CJK-rich lines %d" % (len(lines), len(cjk)))
for i,l in cjk[:15]:
    print("  L%-5d %s" % (i, l[:80]))
