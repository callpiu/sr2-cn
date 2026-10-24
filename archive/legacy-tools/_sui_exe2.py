import re

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
b = open(G + 'SR2_pc.exe', 'rb').read()
print('=== 1) 所有以 _SP 结尾的 ASCII tag ===')
c = set(re.findall(rb'[A-Z][A-Z0-9_]{4,50}', b))
sp = sorted(x.decode() for x in c if x.endswith(b'_SP'))
print('count', len(sp))
for s in sp:
    print('   ', s)

print()
print('=== 2) 所有含 LAN 的 ASCII tag ===')
lan = sorted(x.decode() for x in c if b'LAN' in x)
for s in lan:
    print('   ', s)

print()
print('=== 3) 所有含 SPLASH / SP 界面的 tag ===')
for s in sorted(x.decode() for x in c if b'SPLASH' in x):
    print('   ', s)

print()
print('=== 4) SUI 开头的 tag（全文件）===')
sui = sorted(x.decode() for x in c if x.startswith(b'SUI'))
print('count', len(sui))
for s in sui:
    print('   ', s)

print()
print('=== 5) DFEngine.dll 里的 SUI_PLATFORM 上下文 ===')
d = open(G + 'DFEngine.dll', 'rb').read()
i = d.find(b'SUI_PLATFORM')
print('offset', hex(i))
print(repr(d[i - 120:i + 120]))