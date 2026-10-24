import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"

# candidate hashes -> label
cands={
 0x36b05984:"弹药(独立标签)",
 0xe95b23d1:"当前弹药",
 0xa4443217:"手枪弹药",
 0x5f74328a:"步枪弹药",
 0x68167528:"霰弹枪弹药",
 0xc7a9987d:"冲锋枪弹药",
 0x921ffa90:"狙击弹药",
 0x64630880:"RPG 弹药",
 0x3fbc42ec:"火焰弹药",
 0x0c53a954:"无限弹药",
 0x366f72ca:"额外弹药",
 0x04427079:"你要拿“%s”弹药吗？",
}
for vp_path,label in [(game+"patch.vpp_pc","PATCH"),(game+"common.vpp_pc","COMMON")]:
    vp=S.Vpp(vp_path)
    for e in vp.entries():
        if e['ext'].lower()!='xtbl': continue
        n=e['name']
        buf=vp.read(e)
        for h,lab in cands.items():
            if struct.pack('<I',h) in buf:
                print(f"{label} {n}.xtbl  ->  {lab} ({h:#010x})")
