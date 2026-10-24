import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
loose = open(r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/patch_ch.le_strings","rb").read()
print("松散 patch_ch.le_strings: %d 字节" % len(loose))
# VPP 内同名条目
for tag,p in (("原始 patch.vpp_pc", r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig"),
              ("当前 patch.vpp_pc", os.path.join(G,"patch.vpp_pc"))):
    v=Vpp(p); e=v.find("patch_ch","le_strings")
    if e:
        b=v.read(e)
        print("  %-18s patch_ch.le_strings = %d 字节, 与松散版相同=%s" % (tag, len(b), b==loose))
    else:
        print("  %-18s 无 patch_ch 条目" % tag)
def cl(p):
    v=Vpp(p); t=v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
no = cl(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
nm = cl(os.path.join(G,"patch.vpp_pc"))
n = struct.unpack_from('<I', loose, 8)[0]
print("\n松散文件条目数 n=%d, 正文起点=%d" % (n, 12+n*8+1))
txt = loose[12+n*8+1:]
codes = struct.unpack_from('<%dH'%(len(txt)//2), txt, 0)
for tag, nums in (("用官方字符表解", no), ("用我的字符表解", nm)):
    out=[]
    for c in codes[:70]:
        out.append('|' if c==0 else ('<%d>'%c if c<32 else (chr(nums[c-32]) if c-32<len(nums) else '{%d}'%c)))
    print("  %s: %s" % (tag, "".join(out)))
