import sys, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
v = S.Vpp(game+"common.vpp_pc")
txts=[]
for e in v.entries():
    n = e['name']+(("."+e['ext']) if e['ext'] else '')
    if e['ext'].lower()=='txt' or re.search(r'char|list|jpn|jp|chin|font', n, re.I):
        txts.append((n,e['size']))
print("common.vpp_pc candidate charlist/font entries:")
for n,s in sorted(txts):
    print(f"  {n:45s} {s}")
print("total entries in common:", v.num)
