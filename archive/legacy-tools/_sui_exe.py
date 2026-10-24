import os, struct

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
files = ['SR2_pc.exe', 'DFEngine.dll']

probes = ['SUI_LAN_COOP_SP', 'SUI_LAN', 'COOP_SP', 'SUI_']

for f in files:
    p = G + f
    if not os.path.exists(p):
        print(f, 'MISSING')
        continue
    b = open(p, 'rb').read()
    print('=== %s  size=%d' % (f, len(b)))
    for pr in probes:
        raw = b.count(pr.encode())
        be = b.count(pr.encode('utf-16-be'))
        le = b.count(pr.encode('utf-16-le'))
        print('   %-16s raw=%d  utf16be=%d  utf16le=%d' % (pr, raw, be, le))

    # 反向：搜 'SUI' 附近是否有 tag 池
    print('   -- 类似 _UI_ / _SP 的 tag 池探测 --')
    import re
    # ASCII 连续大写+下划线+数字 >=6 字符
    cands = set(re.findall(rb'[A-Z][A-Z0-9_]{5,40}', b))
    sui = [c.decode() for c in cands if b'SUI' in c or c.startswith(b'COOP') or c.endswith(b'_SP')]
    print('   ASCII tag-like count:', len(cands), ' SUI/COOP/_SP 相关:', len(sui))
    for c in sorted(sui)[:40]:
        print('      ', c)
    # utf16be tag 池
    cands2 = set(re.findall(rb'(?:[A-Z][\x00][A-Z0-9_][\x00]){4,40}', b))
    print('   utf16be tag-like count:', len(cands2))
    dec = []
    for c in cands2:
        try:
            s = c.decode('utf-16-le')
        except Exception:
            continue
        if 'SUI' in s or 'COOP' in s or s.endswith('_SP'):
            dec.append(s)
    for s in sorted(set(dec))[:40]:
        print('      ', s)
    print()