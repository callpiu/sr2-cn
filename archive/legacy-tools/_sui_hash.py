import zlib, struct

def crc32(s):
    return zlib.crc32(s.encode()) & 0xFFFFFFFF

def fnv1a32(s):
    h = 0x811C9DC5
    for c in s.encode():
        h ^= c
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h

def fnv1_32(s):
    h = 0x811C9DC5
    for c in s.encode():
        h = (h * 0x01000193) & 0xFFFFFFFF
        h ^= c
    return h

def djb2(s):
    h = 5381
    for c in s.encode():
        h = ((h * 33) + c) & 0xFFFFFFFF
    return h

def djb2x(s):
    h = 5381
    for c in s.encode():
        h = ((h * 33) ^ c) & 0xFFFFFFFF
    return h

def sdbm(s):
    h = 0
    for c in s.encode():
        h = (c + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h

def jenkins(s):
    h = 0
    for c in s.encode():
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= (h >> 6)
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= (h >> 11)
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h

def elf(s):
    h = 0
    for c in s.encode():
        h = ((h << 4) + c) & 0xFFFFFFFF
        g = h & 0xF0000000
        if g:
            h ^= g >> 24
        h &= ~g & 0xFFFFFFFF
    return h

def bkdr(s):
    h = 0
    for c in s.encode():
        h = (h * 131 + c) & 0xFFFFFFFF
    return h

def rs(s):
    b = s.encode()
    a, bb = 63689, 378551
    for c in b:
        a = (a * 33 + c) & 0xFFFFFFFF
        bb = (bb * 65599 + c) & 0xFFFFFFFF
    return a

FUNCS = [('crc32', crc32), ('fnv1a32', fnv1a32), ('fnv1_32', fnv1_32),
         ('djb2', djb2), ('djb2x', djb2x), ('sdbm', sdbm), ('jenkins', jenkins),
         ('elf', elf), ('bkdr', bkdr), ('rs', rs)]

# 已知配对（CH 记录 ID <-> US 原文）
KNOWN = [
    ('39C7759B', 'Waiting for Player...', '等待玩家……'),
    ('3CAB6F69', 'Waiting for Players', '等待玩家'),
    ('12012AE5', 'Single Player', '单人游戏'),
]

print('=== 用已知 tag 试hash ===')
probes = ['MULTI_COOP_WAITING_PLAYER_2', 'MULTI_COOP_WAITING_PLAYER',
          'WAITING_FOR_PLAYER', 'SINGLE_PLAYER']

for h, en, zh in KNOWN:
    print('\n目标 %s  (%s)' % (h, en))
    for nm, f in FUNCS:
        for tag in probes:
            v = f(tag)
            if v == int(h, 16):
                print('   *** MATCH %s(%s) = %08X' % (nm, tag, v))
        # 也打印几个供参考
    print('   候选值:')
    for nm, f in FUNCS:
        print('      %-10s %s  %08X' % (nm, probes[0], f(probes[0])))

print()
print('=== 直接看已知 tag 名能不能算出ID：试更多变体 ===')
alltags = ['MULTI_COOP_WAITING_PLAYER_2', 'MULTI_COOP_WAITING_PLAYER',
           'MULTI_MODE_5', 'MULTI_PLAYER', 'SUI_LAN_COOP_SP',
           'LEADERBOARDS_SP', 'COOP_WAIT']
for t in alltags:
    print(' %-28s' % t, ' '.join('%s=%08X' % (n[:6], f(t)) for n, f in FUNCS[:4]))