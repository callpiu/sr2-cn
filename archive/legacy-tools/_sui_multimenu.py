import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

for e in v.entries():
    nm = e['name'] + '.' + e['ext']
    if 'MultiMenu_text' in nm:
        data = v.read(e)
        print('===', nm, 'size', len(data))
        txt = data.decode('latin1')
        open('F:/sr2-cn/_MultiMenu_text.xml', 'w', encoding='utf-8', errors='replace').write(txt)
        # 打印所有 SUI_ / LAN / COOP 相关片段
        for kw in ['SUI_', 'LAN', 'COOP_LOAD_EXPLANATION', 'COOP_WAIT', 'COOP_TITLE', 'SPLASH']:
            print()
            print('--- %s ---' % kw)
            for m in re.finditer(re.escape(kw), txt):
                a = max(0, m.start() - 300)
                print('   ...%s...' % txt[a:m.end() + 300])
                print()