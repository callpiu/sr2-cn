import struct, os
def hdr(p):
    d=open(p,'rb').read(0x2000)
    o=5+0x14F
    num,cs,lo,lf,le = struct.unpack_from('<iiiii', d, o)
    return num,cs,lo,lf,le,os.path.getsize(p)
for tag,p in (("原始 textures.vpp_pc", r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig"),
              ("当前 textures.vpp_pc", r"G:/SteamLibrary/steamapps/common/Saints Row 2/textures.vpp_pc"),
              ("原始 patch.vpp_pc",   r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"),
              ("当前 patch.vpp_pc",   r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")):
    num,cs,lo,lf,le,sz = hdr(p)
    print("%-22s num=%6d container_size=%12d len_off=%d len_fn=%d len_ext=%d  文件=%12d  差=%d"
          % (tag,num,cs,lo,lf,le,sz,sz-cs))
