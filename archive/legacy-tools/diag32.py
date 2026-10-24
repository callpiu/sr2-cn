# -*- coding: utf-8 -*-
# search codepoint forms of the subtitle text across ALL game files
import os

ROOT = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
TEXTS = ['弟兄们', '免遭袭击', '保护他们免遭', '谈几笔生意']
PATS = {}
for t in TEXTS:
    PATS['u16be_' + t] = t.encode('utf-16-be')
    PATS['u16le_' + t] = t.encode('utf-16-le')
    PATS['utf8_' + t] = t.encode('utf-8')
    try:
        PATS['gbk_' + t] = t.encode('gbk')
    except Exception:
        pass

CHUNK = 8 * 1024 * 1024
OVER = 32
hits = {}
total = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        fp = os.path.join(dirpath, fn)
        try:
            sz = os.path.getsize(fp)
        except OSError:
            continue
        found = []
        try:
            with open(fp, 'rb') as f:
                prev = b''
                pos = 0
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    buf = prev + chunk
                    for name, p in PATS.items():
                        start = 0
                        while True:
                            k = buf.find(p, start)
                            if k < 0:
                                break
                            found.append((name, pos - len(prev) + k))
                            start = k + 1
                    prev = buf[-OVER:]
                    pos += len(chunk)
        except OSError:
            continue
        total += sz
        if found:
            hits[fp] = found

print('scanned %.2f GB' % (total / 1e9))
for fp, lst in sorted(hits.items()):
    print('==', fp.replace(ROOT, ''))
    for name, off in lst[:30]:
        print('   %s @ 0x%X' % (name, off))
if not hits:
    print('NO HITS')
