import sys, struct
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
import numpy as np
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")
def vinfo(name):
    e=vp.find(name,"vf3_pc"); buf=vp.read(e)
    cnt=struct.unpack_from('<I',buf,8)[0]
    recsz=0xD0+cnt*16
    tail=buf[recsz:]
    print(f"\n{name}: size={len(buf)} count={cnt} recsz={recsz} tail={len(tail)} tail/8={len(tail)/8:.2f}")
    for k in [0,32,94,100,500,2000,2794]:
        o=0xD0+k*16
        f=struct.unpack_from('<IIII',buf,o)
        uv=struct.unpack_from('<ff',tail,k*8) if k*8+8<=len(tail) else None
        print(f"  g{k:4d} rec={f} uv={uv}")
vinfo("fnt_chinese")
# common font in common.vpp_pc
vc=S.Vpp(game+"common.vpp_pc")
e=vc.find("fnt_chinese","vf3_pc"); buf=vc.read(e)
cnt=struct.unpack_from('<I',buf,8)[0]
recsz=0xD0+cnt*16; tail=buf[recsz:]
print(f"\nCOMMON fnt_chinese: size={len(buf)} count={cnt} recsz={recsz} tail={len(tail)} tail/8={len(tail)/8:.2f}")
for k in [0,32,94,100,500,2000,2837]:
    o=0xD0+k*16
    f=struct.unpack_from('<IIII',buf,o)
    uv=struct.unpack_from('<ff',tail,k*8)
    print(f"  g{k:4d} rec={f} uv={uv}")
