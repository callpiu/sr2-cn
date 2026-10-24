import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vc=S.Vpp(game+"common.vpp_pc")
for name in ["store_weapons","ammo"]:
    e=vc.find(name,"xtbl"); buf=vc.read(e)
    print(f"\n===== {name}.xtbl  size={len(buf)} =====")
    # extract ascii strings len>=4
    strs=re.findall(rb'[\x20-\x7e]{4,}', buf)
    seen=[]
    for s in strs:
        t=s.decode('ascii')
        if t not in seen: seen.append(t)
    for t in seen[:80]:
        print("  ",t)
