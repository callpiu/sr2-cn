import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
txt = v.read(v.find('dialog_box', 'lua')).decode('latin1')
open('F:/sr2-cn/_dialog_box.lua', 'w', encoding='utf-8', errors='replace').write(txt)

print('=== dialog_box 里所有 text_tag 设置 ===')
for m in re.finditer(r'text_tag"?\s*[,\)]?\s*[^,)\n]*', txt):
    a = max(0, m.start() - 120)
    print('   ...%s...' % txt[a:m.end() + 120].replace('\n', ' '))
    print()

print('=== 所有 SUI_ / SUI 拼接 ===')
for m in re.finditer(r'SUI', txt):
    a = max(0, m.start() - 250)
    print('   @%d ...%s...' % (m.start(), txt[a:m.end() + 250].replace('\n', ' ')))
    print()

print('=== 搜 "LAN" 全部 ===')
for m in re.finditer(r'LAN', txt):
    a = max(0, m.start() - 200)
    print('   @%d ...%s...' % (m.start(), txt[a:m.end() + 200].replace('\n', ' ')))
    print()