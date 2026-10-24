"""diag19: byte-search game files for the ORIGINAL homies text to find the
subtitle's real source (NOT static_CH). Patterns built from charlist indices."""
import os, struct, sys
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
patch = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
clbuf = patch.read(patch.find('charlist_CH', 'txt'))
text = clbuf.decode('ascii', 'replace')
end = text.find('//ENDOFFILE')
CPS = [int(x) for x in text[:end].split() if x.isdigit()]
CP2IDX = {cp: i for i, cp in enumerate(CPS)}

def slot_bytes(s):
    return b''.join(struct.pack('>H', CP2IDX[ord(c)] + 0x20) for c in s)

def cp_bytes(s):
    return b''.join(struct.pack('>H', ord(c)) for c in s)

PATS = {}
for phrase in ['免遭袭击', '弟兄们', '谈几笔生意', '需要你的保护']:
    PATS['SLOT ' + phrase] = slot_bytes(phrase)
    PATS['CP   ' + phrase] = cp_bytes(phrase)

for k, v in PATS.items():
    print(k, v.hex())

SKIP_BIG = True  # pass 1: files <= 60MB only

def scan_file(path, chunk=1 << 20, overlap=32):
    hits = []
    try:
        if SKIP_BIG and os.path.getsize(path) > 60 * 1024 * 1024:
            return hits
        with open(path, 'rb') as f:
            prev = b''; base = 0
            while True:
                buf = f.read(chunk)
                if not buf:
                    break
                data = prev + buf
                for name, pat in PATS.items():
                    i = data.find(pat)
                    while i != -1:
                        hits.append((name, base - len(prev) + i))
                        i = data.find(pat, i + 1)
                prev = data[-overlap:]; base += len(buf)
    except OSError:
        pass
    return hits

files = []
for root, dirs, fnames in os.walk(GAME):
    if 'reshade-shaders' in root:
        continue
    for fn in fnames:
        files.append(os.path.join(root, fn))

print('\ntotal files:', len(files))
scanned = 0
for path in files:
    if SKIP_BIG and os.path.getsize(path) > 60 * 1024 * 1024:
        continue
    scanned += 1
    hits = scan_file(path)
    for name, off in hits:
        print('HIT  %-46s off=%-12d %s' % (os.path.relpath(path, GAME), off, name))
print('scanned %d files (<=60MB).' % scanned)
