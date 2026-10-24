# -*- coding: utf-8 -*-
"""
反推 SR2 的 tag -> 16位 hash 函数。
锚点：用户内存扫描得到
  h=1896  →  「?傲OpenSpy卧?」  ≈ MULTI_LOG_INTO_GAMESPY（登录 OpenSpy）
  h=1EEE  →  「?扰 OpenSpy 地?一」≈ MULTI_GAMESPY_ID（GameSpy ID 标题）
试各种 16 位 hash 算法，看哪个能让候选 tag 落到 0x1896 / 0x1EEE。
"""
import sys, zlib, binascii

TAGS = [
    'MULTI_LOG_INTO_GAMESPY',
    'MULTI_GAMESPY_ID',
    'MULTI_LOG_CREATE_ACCOUNT',
    'MULTI_GAMESPY_EMAIL',
    'MULTI_GAMESPY_PASS',
    'MULTI_GAMESPY_NAME',
    'MAIN_MENU_MULTIPLAYER_SIGN_IN',
    'MULTI_LOGOUT_GAMESPY',
]
T1, T2 = 0x1896, 0x1EEE

def crc16(data, poly, init, refin, refout, xorout):
    if refin:
        crc = init
        for b in data:
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ (poly if crc & 1 else 0)
    else:
        crc = init
        for b in data:
            crc ^= b << 8
            for _ in range(8):
                crc = ((crc << 1) ^ poly) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    if refout:
        crc = int('{:016b}'.format(crc)[::-1], 2)
    return crc ^ xorout

ALGOS = {}
for name, (poly, init, refin, refout) in {
    'IBM': (0xA001, 0x0000, True, True),
    'CCITT': (0x1021, 0xFFFF, False, False),
    'CCITT0': (0x1021, 0x0000, False, False),
    'X25': (0x8408, 0xFFFF, True, True),
    'MAXIM': (0xA001, 0x0000, True, True),
    'DNP': (0xA6BC, 0x0000, True, True),
    'USB': (0xA001, 0xFFFF, True, True),
}.items():
    for xo in (0x0000, 0xFFFF):
        ALGOS['%s/xo%04X' % (name, xo)] = (
            lambda d, p=poly, i=init, ri=refin, ro=refout, x=xo: crc16(d, p, i, ri, ro, x))

def sum16(d): return sum(d) & 0xFFFF
def djb2(d):
    h = 5381
    for b in d: h = ((h << 5) + h + b) & 0xFFFFFFFF
    return h & 0xFFFF
def djb2x(d):
    h = 5381
    for b in d: h = ((h << 5) ^ h) + b & 0xFFFFFFFF
    return h & 0xFFFF
def sdbm(d):
    h = 0
    for b in d: h = (b + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h & 0xFFFF
def fnv1a(d):
    h = 0x811C9DC5
    for b in d: h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h & 0xFFFF
def fnv1(d):
    h = 0x811C9DC5
    for b in d: h = ((h * 0x01000193) & 0xFFFFFFFF) ^ b
    return h & 0xFFFF
def jenkins(d):
    h = 0
    for b in d:
        h = (h + b) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= (h >> 6)
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= (h >> 11)
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h & 0xFFFF
def elf(d):
    h = 0
    for b in d:
        h = ((h << 4) + b) & 0xFFFFFFFF
        g = h & 0xF0000000
        if g: h ^= g >> 24
        h &= ~g & 0xFFFFFFFF
    return h & 0xFFFF
def bkdr(d):
    seed = 131
    h = 0
    for b in d: h = (h * seed + b) & 0xFFFFFFFF
    return h & 0xFFFF
def rs(d):
    a = 63689; bb = 378551; h = 0
    for b in d:
        h = (h * a + b) & 0xFFFFFFFF
        a = (a * bb) & 0xFFFFFFFF
    return h & 0xFFFF
def crc32_lo(d): return zlib.crc32(d) & 0xFFFF
def adler(d): return zlib.adler32(d) & 0xFFFF

for n, f in [('sum16', sum16), ('djb2', djb2), ('djb2x', djb2x), ('sdbm', sdbm),
             ('fnv1a', fnv1a), ('fnv1', fnv1), ('jenkins', jenkins), ('elf', elf),
             ('bkdr', bkdr), ('rs', rs), ('crc32', crc32_lo), ('adler', adler)]:
    ALGOS[n] = f

print('=== 各算法对候选 tag 的输出，找 0x1896 / 0x1EEE ===')
found = False
for name, fn in ALGOS.items():
    for t in TAGS:
        for enc in (t.encode(), t.lower().encode(), t.encode('utf-16-le')):
            h = fn(enc)
            if h in (T1, T2):
                print('  ★ %-14s %-26s -> %04X' % (name, t, h))
                found = True
if not found:
    print('  无命中')
    print()
    print('=== 参考：几个算法的输出分布 ===')
    for name in ['crc16/IBM/xo0000', 'crc16/CCITT/xo0000', 'fnv1a', 'sdbm', 'sum16']:
        fn = ALGOS[name]
        print('  %-20s' % name, {t[:18]: '%04X' % fn(t.encode()) for t in TAGS[:4]})