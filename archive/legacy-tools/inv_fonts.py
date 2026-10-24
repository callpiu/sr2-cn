import struct, re, sys
sys.path.insert(0, "F:/sr2-cn")
import sr2lib as S

def list_entries(path, pat):
    v = S.Vpp(path)
    out = []
    for e in v.entries():
        n = e['name'] + ('.'+e['ext'] if e['ext'] else '')
        if re.search(pat, n, re.I):
            out.append((n, e['size']))
    return v, out

for path, label in [("G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc","PATCH"),
                    ("G:/SteamLibrary/steamapps/common/Saints Row 2/common.vpp_pc","COMMON")]:
    v, out = list_entries(path, r"charlist|fnt|chinese|japanese|jp|font")
    print(f"\n===== {label} ({path.split('/')[-1]}) matches =====")
    for n,sz in sorted(out):
        print(f"  {n:40s} {sz}")
