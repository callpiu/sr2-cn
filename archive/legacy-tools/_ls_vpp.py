import sys
sys.path.insert(0,"F:/sr2-cn")
from sr2font import Vpp
v=Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
es=v.entries()
print("total entries",len(es))
for e in es:
    if 'le_string' in e['ext'].lower() or 'string' in e['name'].lower() or 'static' in e['name'].lower():
        print(e['name'],'.',e['ext'],'size',e['size'])
