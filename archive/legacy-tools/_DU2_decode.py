import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
def cl(p):
    v=Vpp(p); t=v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
def dec(x, nums, skip, ln=400):
    txt = x[skip:]
    codes = struct.unpack_from('<%dH'%(min(ln,len(txt)//2)), txt, 0)
    out=[]
    for c in codes:
        if c == 0: out.append('|')
        elif c < 32: out.append('<%d>'%c)
        elif c-32 < len(nums): out.append(chr(nums[c-32]))
        else: out.append('{%d}'%c)
    return "".join(out)
AO = (get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"), cl(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"), "原始文件 + 官方字符表")
AM = (get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"), cl(os.path.join(G,"patch.vpp_pc")), "原始文件 + 我的字符表(交叉)")
BM = (get(os.path.join(G,"patch.vpp_pc")), cl(os.path.join(G,"patch.vpp_pc")), "当前文件 + 我的字符表")
for x, nums, tag in (AO, AM, BM):
    n = struct.unpack_from('<I', x, 8)[0]
    for skip in (12+n*8, 12+n*8+1):
        print("=== %s  skip=%d ===" % (tag, skip))
        print("   ", dec(x, nums, skip, 300)[:220])
    print()
