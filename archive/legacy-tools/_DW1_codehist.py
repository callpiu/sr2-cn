import sys, os, struct
from collections import Counter
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
def get(p,name,ext):
    v=Vpp(p); e=v.find(name,ext); return v.read(e) if e else None
def hist(x, nums, tag):
    n = struct.unpack_from('<I', x, 8)[0]
    txt = x[12+n*8+1:]
    m = len(txt)//2
    codes = struct.unpack_from('<%dH'%m, txt, 0)
    c = Counter(codes)
    mx = max(nums)+32
    oor = sum(v for k,v in c.items() if k>mx)
    print("=== %s ===" % tag)
    print("   总码数=%d  最大合法码=%d  越界码个数=%d (%.2f%%)" % (m, mx, oor, 100*oor/max(1,m)))
    print("   码值<32 的个数=%d" % sum(v for k,v in c.items() if k<32))
    print("   码0 个数=%d" % c[0])
    print("   最高频10个码:", [(k,v) for k,v in c.most_common(10)])
    print("   码>3000 的个数:", sum(v for k,v in c.items() if k>3000))
    print()
def cl(p):
    v=Vpp(p); t=v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
hist(get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","static_CH","le_strings"), cl(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"), "原始 static_CH + 官方字符表")
hist(get(os.path.join(G,"patch.vpp_pc"),"static_CH","le_strings"), cl(os.path.join(G,"patch.vpp_pc")), "当前 static_CH + 我的字符表")
