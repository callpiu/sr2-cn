import sys
sys.path.insert(0,"F:/sr2-cn")
from sr2font import Vpp

def load(path, name):
    v=Vpp(path)
    e=v.find(name,'le_strings')
    return v.read(e) if e else None

# game (hanzify) static_CH: is 的 present as UTF-16LE?
g = load(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc","static_CH")
print("game static_CH size", len(g) if g else None)
if g:
    print("  has 的(LE)?", g.find("的".encode('utf-16-le'))>=0, " 保(LE)?", g.find("保".encode('utf-16-le'))>=0)
    # count CJK-range chars when decoded utf-16-le
    txt=g.decode('utf-16-le','ignore')
    cjk=sum(1 for c in txt if 0x4E00<=ord(c)<=0x9FFF)
    print("  CJK chars in utf-16-le decode:", cjk)

# official backup voice_script_CH
b = load(r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/backup_original/patch.vpp_pc","voice_script_CH")
print("backup voice_script_CH size", len(b) if b else None)
if b:
    for kw in ['弟兄','兄弟','保護','保','襲擊','的']:
        for enc in ('be','le'):
            i=b.find(kw.encode('utf-16-'+enc))
            if i>=0:
                print(f"  voice_script_CH [{kw}/{enc}] @{i}: {b[max(0,i-20):i+60].decode('utf-16-'+enc,'replace')!r}")
                break
