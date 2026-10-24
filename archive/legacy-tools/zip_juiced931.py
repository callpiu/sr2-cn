import zipfile, os, hashlib

SRC = 'F:/sr2-cn/_发布包/黑道圣徒2_简体中文_Juice9.3.1_DLC1.0.1_整合包/'
OUT = 'F:/sr2-cn/_发布包/黑道圣徒2_Juiced9.3.1_简体汉化整合_20261018d.zip'

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(SRC):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, SRC).replace('\\', '/')
            z.write(p, rel)

print('built', OUT)
print('size', os.path.getsize(OUT))
print('md5', md5(OUT))

with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    nl = z.namelist()
    print('entries', len(nl))
    need = ['patch.vpp_pc', 'Mods/dialog_box.lua', 'DFEngine.dll',
            'Mods/JUICED - Strings/juiced_CH.le_strings', 'common.vpp_pc',
            'Mods/city_load.lua', 
            'DLC/Text/dlc_ch.le_strings', '_先读我.txt']
    for n in need:
        assert n in nl, 'missing ' + n
    h = hashlib.md5(z.read('patch.vpp_pc')).hexdigest()
    assert h == '8d82233053e1231337eeb84c82d1933b', h
    h2 = hashlib.md5(z.read('Mods/dialog_box.lua')).hexdigest()
    assert h2 == 'f89645e132f3e65bf9284e68ce7de2cc', h2
    h3 = hashlib.md5(z.read('Mods/JUICED - Strings/juiced_CH.le_strings')).hexdigest()
    assert h3 == 'be1c8ed9c0d40ffbf80233600c392ec9', h3
    h3 = hashlib.md5(z.read('common.vpp_pc')).hexdigest()
    assert h3 == 'f041934f15f06c6facc97d00e1ab7efd', h3
    h4 = hashlib.md5(z.read('Mods/city_load.lua')).hexdigest()
    assert h4 == '934b0539e0b2dd5934a27c3484aafdef', h4
    print('in-zip verified: patch.vpp_pc + dialog_box.lua')
    print()
    print('顶层条目:')
    for n in sorted(nl):
        if '/' not in n:
            print('  ', n)
    print()
    print('Mods/ 条目数:', sum(1 for n in nl if n.startswith('Mods/')))
    print('Juiced/ 条目数:', sum(1 for n in nl if n.startswith('Juiced/')))
    print('patches/ 条目数:', sum(1 for n in nl if n.startswith('patches/')))