# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'

def parse(path, text0=0x1364):
    raw = open(path, 'rb').read()
    o = text0
    ents = []
    while o + 4 <= len(raw):
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= len(raw):
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        ents.append((h, ''.join(chr(c) for c in cps)))
    return raw, ents, o

ru, eu, endu = parse(G + 'dlc_us.le_strings')
rc, ec, endc = parse(G + 'dlc_ch.le_strings')
print('us: size=%d 条目=%d 解析终止=%d(差值%d)' % (len(ru), len(eu), endu, len(ru) - endu))
print('ch: size=%d 条目=%d 解析终止=%d(差值%d)' % (len(rc), len(ec), endc, len(rc) - endc))
print('ch 头部 0..0x1364 与 us 相同?', ru[:0x1364] == rc[:0x1364])

du = dict(eu); dc = dict(ec)
print('hash 集合相同?', set(du) == set(dc), ' 条目数', len(du), len(dc))

# 关键 key 对应文本
key_texts = ['Bodies recovered:', 'Kill the Ultor', 'Recover the first set of bodies']
for kt in key_texts:
    for h, t in eu:
        if t.strip() == kt or t == kt:
            print('\nUS :', repr(t[:70]))
            print('CH :', repr(dc.get(h, '<缺失>')[:70]))
            print('hash 0x%08X' % h)
            break

# 统计：ch 中仍与 us 完全相同的条数 / 含中文的条数
same = sum(1 for h in du if du[h] == dc.get(h))
def has_cjk(s):
    return any('一' <= c <= '鿿' for c in s)
cjk = sum(1 for h in dc if has_cjk(dc[h]))
print('\n未译(与英文相同)：%d  含汉字：%d  总条目：%d' % (same, cjk, len(dc)))

# 未译条目里，长文本(>25字符)有多少 —— 这些是主要任务/字幕文本
un = [(h, du[h]) for h in du if du[h] == dc.get(h) and len(du[h]) > 25]
print('未译且长度>25 的条数：', len(un))
for h, t in un[:12]:
    print('   ', repr(t[:80]))
