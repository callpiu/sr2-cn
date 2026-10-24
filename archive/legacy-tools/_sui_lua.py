import re

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
d = open(G + 'DFEngine.dll', 'rb').read()

print('=== DFEngine.dll: 搜 "SUI_" 前后 4KB 的 Lua 代码区 ===')
i = d.find(b'SUI_')
lo = max(0, i - 6000)
hi = min(len(d), i + 6000)
seg = d[lo:hi]
# 提取可打印片段
txt = ''.join(chr(c) if 32 <= c < 127 else '\n' for c in seg)
parts = [p for p in txt.split('\n') if len(p) >= 4]
print('\n'.join(parts[:200]))

print()
print('=== 搜 COOP_ 在 DFEngine.dll ===')
i = 0
n = 0
while True:
    i = d.find(b'COOP_', i)
    if i < 0:
        break
    seg = d[max(0, i - 70):i + 90]
    print('  @%08X %r' % (i, seg))
    n += 1
    i += 4
    if n > 25:
        break
print('COOP_ count', n)

print()
print('=== 搜 _SP 在 DFEngine.dll（ASCII 上下文） ===')
i = 0
n = 0
while True:
    i = d.find(b'_SP', i)
    if i < 0:
        break
    seg = d[max(0, i - 70):i + 70]
    pr = ''.join(chr(c) if 32 <= c < 127 else '.' for c in seg)
    if 'SUI' in pr or 'COOP' in pr or 'LAN' in pr or 'sprintf' in pr or '..' in pr:
        print('  @%08X %s' % (i, pr))
        n += 1
    i += 3
print('filtered _SP count', n)