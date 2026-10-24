import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
a=get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
b=get(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
for tag,x in (("原始",a),("当前",b)):
    magic=x[:4]; f2=struct.unpack_from('<I',x,4)[0]; n=struct.unpack_from('<I',x,8)[0]
    print("=== %s: magic=%s f2=0x%X 条目=%d 目录结束=%d 文件=%d"%(tag,magic.hex(),f2,n,12+n*8,len(x)))
    # 读前几条 (len,id)
    for i in range(3):
        ln,hid = struct.unpack_from('<II', x, 12+i*8)
        print("   entry%d len=%d id=0x%X"%(i,ln,hid))
    txt = x[12+n*8:]
    print("   正文长度=%d 首32字节=%s" % (len(txt), txt[:32].hex()))
    u16 = txt[:60].decode('utf-16-le','replace')
    print("   按UTF-16LE: %r" % u16[:40])
