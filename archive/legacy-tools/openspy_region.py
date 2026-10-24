# -*- coding: utf-8 -*-
"""精读 59CCF3xx / 59CCF5xx 区域：这里是 OpenSpy 相关字符串的集中地"""
import sys, struct, time, os
sys.path.insert(0, 'F:/sr2-cn')
import ce_mini as C

C.CL = C.load_charlist()
CL = C.CL

def dump_region(h, base, length):
    raw = C.read_mem(h, base, length)
    if not raw:
        return None
    return raw

def uni(raw):
    out = []
    for i in range(0, len(raw) - 1, 2):
        u = struct.unpack_from('<H', raw, i)[0]
        if u == 0:
            out.append('\x00')
        elif 0x20 <= u <= 0x7E:
            out.append(chr(u))
        elif 0x4E00 <= u <= 0x9FFF or 0x3000 <= u <= 0x303F or 0xFF00 <= u <= 0xFFEF \
                or 0x2E80 <= u <= 0x2EFF:
            out.append(chr(u))
        else:
            out.append('<%04X>' % u)
    return ''.join(out)

pid = C.find_pid()
h = C.open_process(pid)
print('pid=%d' % pid)

for tag, base, ln in [('A区 59CCF200', 0x59CCF200, 0x400),
                      ('B区 59D40D00', 0x59D40D00, 0x900),
                      ('C区 56F60C00', 0x56F60C00, 0x300)]:
    raw = dump_region(h, base, ln)
    if not raw:
        print('%s 读取失败' % tag); continue
    print()
    print('=' * 100)
    print('=== %s ===' % tag)
    print('=' * 100)
    t = uni(raw)
    # 按 \x00 分段（字符串以 null 结尾）
    segs = t.split('\x00')
    for s in segs:
        if len(s.strip()) < 2:
            continue
        vis = ''.join(c if (c.isprintable() or c == ' ') else '·' for c in s)
        print('  %r' % vis)
    print()
    print('  --- hex（每 32 字节一行，仅显示有可读内容的）---')
    for off in range(0, len(raw), 64):
        chunk = raw[off:off + 64]
        try:
            s2 = uni(chunk)
        except Exception:
            continue
        readable = sum(1 for c in s2 if c.isprintable() and c != ' ')
        if readable > 6:
            print('   %08X  %s' % (base + off, ' '.join('%04X' % struct.unpack_from('<H', chunk, i)[0]
                                                for i in range(0, len(chunk) - 1, 2))))