import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
def load(p):
    v=Vpp(p); b=bytes(v.read(v.find("fnt_chinese","vf3_pc")))
    N=struct.unpack_from("<i",b,0x08)[0]
    return b,N
b0,N0 = load(os.path.join(W,"pristine","patch.vpp_pc"))
b3,N3 = load(os.path.join(W,"_juice_fix","patch.vpp_pc"))
CH0=0xD0
print("=== 头部参数对比 ===")
for o,nm in ((0x04,"Version"),(0x08,"NumChars"),(0x0C,"FirstAscii"),(0x10,"Width"),
             (0x14,"Height(i16)"),(0x16,"RenderHeight(i16)"),(0x18,"BaselineOffset"),
             (0x1C,"CharacterSpacing"),(0x20,"KernPairCount"),(0x24,"VerticalOffset")):
    a=struct.unpack_from("<i",b0,o)[0]; b=struct.unpack_from("<i",b3,o)[0]
    print("  %-20s 原厂 %-8d 第三方 %-8d %s" % (nm,a,b,"" if a==b else "  <-- 不同"))
print()
print("=== 记录字段对比（同一字符：'A'）===")
CPS0=[int(l) for l in Vpp(os.path.join(W,"pristine","patch.vpp_pc")).read(Vpp(os.path.join(W,"pristine","patch.vpp_pc")).find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("原厂 'A' 索引 %d, 第三方 'A' 索引 %d" % (CPS0.index(65), 65-32))
for tag,b in (("原厂",b0),("第三方",b3)):
    for i,ch in ((CPS0.index(65),"A"),(CPS0.index(0x4F5C) if 0x4F5C in CPS0 else 500,"作")):
        pass
for tag,b,CPS in (("原厂",b0,CPS0),("第三方",b3,[int(l) for l in Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc")).read(Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc")).find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()])):
    print("  %s:" % tag)
    for ch in "A n 作":
        if ord(ch) not in CPS: continue
        i=CPS.index(ord(ch))
        r=struct.unpack_from("<8h", b, CH0+i*16)
        print("    %-3r 索引%-5d %s" % (ch,i," ".join("%6d"%x for x in r)))
