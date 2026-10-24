# -*- coding: utf-8 -*-
# Exhaustive search: EVERY file under game dir, any size.
# Patterns:
#   hash bytes of 0x84F287ED -> ED 87 F2 84 ; 0x10AF1E62 -> 62 1E AF 10
#   slot BE bytes: 弟兄们 = 04 2B 01 C6 01 6C ; 免遭袭击 = 01 CC 0A 03 09 08 01 FF
import os, sys

ROOT = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATS = {
    'HASH_84F287ED': bytes.fromhex('ed87f284'),
    'HASH_10AF1E62': bytes.fromhex('621eaf10'),
    'SLOT_弟兄们':   bytes.fromhex('042b01c6016c'),
    'SLOT_免遭袭击': bytes.fromhex('01cc0a03090801ff'),
}
CHUNK = 8 * 1024 * 1024
OVER = 16

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
        except OSError as e:
            print('SKIP', fp, e)
            continue
        total += sz
        if found:
            hits[fp] = found

print('scanned %.2f GB' % (total / 1e9))
for fp, lst in hits.items():
    print('==', fp.replace(ROOT, ''))
    for name, off in lst[:20]:
        print('   %s @ 0x%X (%d)' % (name, off, off))
    if len(lst) > 20:
        print('   ... %d more' % (len(lst) - 20))
if not hits:
    print('NO HITS ANYWHERE')
