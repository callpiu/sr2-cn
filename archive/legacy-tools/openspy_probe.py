# -*- coding: utf-8 -*-
"""
OpenSpy 界面错位字定位器（专用版）
在 SR2_pc.exe 内存里搜「OpenSpy」的所有形态，把命中点周围的 slot 序列
用 charlist_CH 解码，直接看出「登录」两个字在内存里的真实形态。

用法：
    1) 启动游戏，停在主菜单即可（不必进联机页）
    2) python openspy_probe.py            # 扫描
    3) python openspy_probe.py wait       # 等游戏出现再扫（可先开脚本再进游戏）
    4) python openspy_probe.py dump ADDR  # 看某处细节
"""
import sys, os, struct, time
sys.path.insert(0, 'F:/sr2-cn')
import ce_mini as C

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
C.CL = C.load_charlist()
CL = C.CL
print('charlist_CH: %d 项' % len(CL))

def dec(raw, big=False):
    """slot 字节流 -> 文本"""
    fmt = '>H' if big else '<H'
    out = []
    for i in range(0, len(raw) - 1, 2):
        s = struct.unpack_from(fmt, raw, i)[0]
        if s == 0:
            out.append('<END>')
        elif 0x20 <= s <= 0x7E:
            out.append(chr(s))
        else:
            ci = s - 0x20
            out.append(chr(CL[ci]) if 0 <= ci < len(CL) else '<%#x>' % s)
    return ''.join(out)

PATTERNS = [
    ('UTF16LE_mixed', 'OpenSpy'.encode('utf-16-le')),
    ('UTF16LE_UPPER', 'OPENSPY'.encode('utf-16-le')),
    ('UTF16BE_mixed', 'OpenSpy'.encode('utf-16-be')),
    ('UTF16BE_UPPER', 'OPENSPY'.encode('utf-16-be')),
    ('ASCII', b'OpenSpy'),
    ('ASCII_UPPER', b'OPENSPY'),
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

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    if cmd == 'wait':
        while True:
            pid = C.find_pid()
            if pid:
                print('找到游戏 pid=%d' % pid)
                break
            print('等待游戏启动...')
            time.sleep(3)
    pid = C.find_pid()
    if not pid:
        print('★ 未找到 SR2_pc.exe —— 请先启动游戏')
        return
    h = C.open_process(pid)
    if not h:
        print('★ 无法打开进程')
        return
    limit = C.addr_limit(C.is_wow64(h))
    print('进程 pid=%d 已打开，扫描上限 %#x' % (pid, limit))
    t0 = time.time()
    hits = scan_all(h, limit)
    print('扫描耗时 %.1f 秒，共 %d 处命中' % (time.time() - t0, len(hits)))

    print()
    print('=== 各形态命中数 ===')
    from collections import Counter
    c = Counter(nm for nm, a in hits)
    for nm in PATTERNS:
        print('  %-14s %d' % (nm, c.get(nm[0], 0)))

    print()
    print('=== 命中详情（解码上下文）===')
    seen = set()
    lines = []
    for nm, addr in hits:
        key = addr & ~0x3F
        if key in seen:
            continue
        seen.add(key)
        try:
            raw = C.read_mem(h, addr - 96, 240)
        except Exception:
            continue
        le_t = dec(raw, False)
        be_t = dec(raw, True)
        print()
        print('--- %s @ %08X ---' % (nm, addr))
        for tag, t in (('LE', le_t), ('BE', be_t)):
            up = t.upper()
            p = up.find('OPENSPY')
            if p >= 0:
                lo = max(0, p - 14)
                print('    %s: %r' % (tag, t[lo:p + 16]))
            else:
                print('    %s: %r' % (tag, t[:70]))
        lines.append('--- %s @ %08X ---\n  LE: %r\n  BE: %r\n  HEX: %s\n'
                     % (nm, addr, le_t, be_t, raw.hex(' ')))

    outdir = 'F:/sr2-cn/_扫描结果'
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, 'openspy_%s.txt' % time.strftime('%Y%m%d_%H%M%S'))
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print()
    print('结果已存:', fn)

if __name__ == '__main__':
    main()