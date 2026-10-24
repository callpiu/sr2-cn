import os, re, glob

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
targets = [b'SUI_LAN_COOP_SP', b'SUI_LAN', b'COOP_SP']

print('=== 全盘扫所有游戏文件（ASCII + UTF16BE/LE） ===')
files = []
for root, dirs, fns in os.walk(G):
    for fn in fns:
        files.append(os.path.join(root, fn))
print('total files', len(files))

for p in files:
    try:
        sz = os.path.getsize(p)
        if sz > 200 * 1024 * 1024:
            # 大文件分段读
            found = False
            with open(p, 'rb') as f:
                prev = b''
                while True:
                    chunk = f.read(1 << 24)
                    if not chunk:
                        break
                    buf = prev + chunk
                    for t in targets:
                        i = buf.find(t)
                        if i >= 0 and not found:
                            print('HIT %s  %s @chunk+%08X (size=%d)' % (os.path.basename(p), t.decode(), i, sz))
                            found = True
                    prev = chunk[-64:]
            continue
        b = open(p, 'rb').read()
    except Exception:
        continue
    for t in targets:
        for enc, nm in [(lambda x: x, 'raw'), (lambda x: x, 'x')]:
            pass
        c1 = b.count(t)
        c2 = b.count(t.decode().encode('utf-16-be'))
        c3 = b.count(t.decode().encode('utf-16-le'))
        if c1 or c2 or c3:
            print('HIT %-40s %-18s raw=%d be=%d le=%d' % (os.path.basename(p), t.decode(), c1, c2, c3))
            i = b.find(t)
            if i >= 0:
                print('     ctx=%r' % b[max(0, i - 80):i + 100])
print('=== done ===')