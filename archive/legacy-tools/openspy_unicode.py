# -*- coding: utf-8 -*-
"""把内存命中按真 Unicode(LE) 解码，找出「轻傲OPENSPY卧短」的真实来源"""
import sys, struct, time, os
sys.path.insert(0, 'F:/sr2-cn')
import ce_mini as C

C.CL = C.load_charlist()
CL = C.CL

def dec_unicode(raw):
    """真 Unicode UTF-16LE -> 文本"""
    out = []
    for i in range(0, len(raw) - 1, 2):
        u = struct.unpack_from('<H', raw, i)[0]
        if u == 0:
            out.append('\x00')
        elif 0x20 <= u <= 0x7E:
            out.append(chr(u))
        elif 0x4E00 <= u <= 0x9FFF or 0x3000 <= u <= 0x303F or 0xFF00 <= u <= 0xFFEF:
            out.append(chr(u))
        else:
            out.append('?')
    return ''.join(out)

PATTERNS = [
    ('LE_mixed', 'OpenSpy'.encode('utf-16-le')),
    ('LE_UPPER', 'OPENSPY'.encode('utf-16-le')),
]

def scan_all(h, max_addr):
    hits = []
    for base, size, protect in C.enum_regions(h, max_addr):
        try:
            data = C.read_mem(h, base, size)
        except Exception:
            continue
        if not data:
            continue
        for nm, pat in PATTERNS:
            i = 0
            while True:
                i = data.find(pat, i)
                if i < 0:
                    break
                hits.append((nm, base + i))
                i += 1
    return hits

pid = C.find_pid()
if not pid:
    print('★ 游戏未运行'); sys.exit(1)
h = C.open_process(pid)
limit = C.addr_limit(C.is_wow64(h))
print('pid=%d 扫描...' % pid)
hits = scan_all(h, limit)
print('命中 %d 处' % len(hits))

print()
print('=== 按真 Unicode(LE) 解码每个命中点前后 ===')
lines = []
for nm, addr in hits:
    try:
        raw = C.read_mem(h, addr - 120, 300)
    except Exception:
        continue
    t = dec_unicode(raw)
    # 清理不可见字符
    vis = ''.join(c if (c.isprintable() or c == ' ') else '·' for c in t)
    p = vis.upper().find('OPENSPY')
    ctx = vis[max(0, p - 20):p + 20] if p >= 0 else vis[:60]
    print()
    print('--- %s @ %08X ---' % (nm, addr))
    print('   %r' % ctx)
    lines.append('%s @ %08X\n  %r\n' % (nm, addr, ctx))

outdir = 'F:/sr2-cn/_扫描结果'
os.makedirs(outdir, exist_ok=True)
fn = os.path.join(outdir, 'openspy_unicode_%s.txt' % time.strftime('%Y%m%d_%H%M%S'))
open(fn, 'w', encoding='utf-8').write('\n'.join(lines))
print()
print('已存:', fn)