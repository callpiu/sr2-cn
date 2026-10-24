import sys
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp = S.Vpp(game+"patch.vpp_pc")
e = vp.find("charlist_CH")
print("entry:", e['name'], e['ext'], e['size'] if e else None)
if e:
    buf = vp.read(e)
    print("first 120 bytes:", buf[:120])
