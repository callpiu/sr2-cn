import re

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
d = open(G + 'DFEngine.dll', 'rb').read()
b = open(G + 'SR2_pc.exe', 'rb').read()

print('=== DFEngine.dll 中所有 SUI_ 前缀用法（含字符串） ===')
i = 0
while True:
    i = d.find(b'SUI_', i)
    if i < 0:
        break
    seg = d[max(0, i - 80):i + 120]
    print('  @%08X  %r' % (i, seg))
    print()
    i += 4

print()
print('=== SR2_pc.exe 中 SUI_ 用法 ===')
i = 0
n = 0
while True:
    i = b.find(b'SUI_', i)
    if i < 0:
        break
    seg = b[max(0, i - 60):i + 100]
    printable = ''.join(chr(c) if 32 <= c < 127 else '.' for c in seg)
    print('  @%08X  %s' % (i, printable))
    n += 1
    i += 4
print('total SUI_ in exe:', n)