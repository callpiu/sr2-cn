import sys, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
pat=re.compile(r'fire|store|shop|weapon|ammo|buy|purchase|merch|friendly',re.I)
for path,label in [(game+"patch.vpp_pc","PATCH"),(game+"common.vpp_pc","COMMON")]:
    vp=S.Vpp(path)
    names=[e['name']+("."+e['ext'] if e['ext'] else '') for e in vp.entries() if e['ext'].lower()=='xtbl' and pat.search(e['name'])]
    print(f"\n{label} shop-ish xtbl ({len(names)}):")
    for n in sorted(names)[:60]: print("  ",n)
