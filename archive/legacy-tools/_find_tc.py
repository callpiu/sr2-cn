import sys
sys.path.insert(0,"F:/sr2-cn")
from sr2font import Vpp

src = r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/backup_original/patch.vpp_pc"
v = Vpp(src)
print("entries", v.num)
e = v.find("static_CH","le_strings")
print("static_CH found:", bool(e), "size", e["size"] if e else None)
if not e: 
    # list le_strings
    for x in v.entries():
        if 'le_string' in x['ext']:
            print("  ", x['name'], x['ext'], x['size'])
    raise SystemExit
d = v.read(e)
print("read", len(d))
# grep 弟兄 / 兄弟 / 保護 / 襲擊 in BE and LE
for name,kw in [('弟兄','弟兄'),('兄弟','兄弟'),('保護','保護'),('襲擊','襲擊'),('生意','生意')]:
    for enc in ('be','le'):
        seq = kw.encode('utf-16-'+enc)
        i = d.find(seq)
        if i>=0:
            s=max(0,i-30); en=min(len(d),i+80)
            print(f"[{name}/{enc}] @{i}: {d[s:en].decode('utf-16-'+enc,'replace')!r}")
