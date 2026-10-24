# -*- coding: utf-8 -*-
"""
用已知 tag 反推 16 位 hash 函数。
候选：SR2 用的是 CRC16 / 或某种简单 hash。
已知锚点（来自游戏内 tag 名，需用户提供验证）。
先枚举常见 16 位 hash 算法，看哪个能把已知 tag 映射到 0x1896 / 0x1EEE。
"""
import struct, sys, re

# 候选的 OpenSpy 相关 tag 名（推测）
CAND = [
    'OP_SP_LOGIN', 'OP_SP_LOGOUT', 'MENU_LOGIN_GAMESPY', 'MENU_LOGOUT_GAMESPY',
    'LOGIN_GAMESPY', 'LOGOUT_GAMESPY', 'MENU_LOGIN', 'MENU_LOGOUT',
    'MP_LOGIN', 'MP_LOGOUT', 'GAMESPY_LOGIN', 'GAMESPY_LOGOUT',
]

def crc16(data, poly=0xA001, init=0x0000, refin=True, refout=True, xorout=0x0000):
    if refin:
        crc = init
        for b in data:
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ (poly if crc & 1 else 0)
        return crc ^ xorout
    else:
        crc = init
        for b in data:
            crc ^= b << 8
            for _ in range(8):
                crc = ((crc << 1) ^ (poly & 0xFFFF)) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
        return crc ^ xorout

def crc16_ccitt(data):
    return crc16(data, poly=0x1021, init=0xFFFF, refin=False, refout=False)

def crc16_ibm(data):
    return crc16(data, poly=0xA001, init=0x0000)

def sum16(data):
    return sum(data) & 0xFFFF

def djb2(data):
    h = 5381
    for b in data:
        h = ((h << 5) + h + b) & 0xFFFFFFFF
    return h & 0xFFFF

def sdbm(data):
    h = 0
    for b in data:
        h = (b + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h & 0xFFFF

def fnv1a(data):
    h = 0x811C9DC5
    for b in data:
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h & 0xFFFF

def fnv1(data):
    h = 0x811C9DC5
    for b in data:
        h = ((h * 0x01000193) & 0xFFFFFFFF) ^ b
    return h & 0xFFFF

def jenkins(data):
    h = 0
    for b in data:
        h = (h + b) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= (h >> 6)
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= (h >> 11)
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h & 0xFFFF

ALGOS = {
    'crc16-ibm': crc16_ibm,
    'crc16-ccitt': crc16_ccitt,
    'crc16-ccitt0': lambda d: crc16(d, poly=0x1021, init=0x0000, refin=False, refout=False),
    'sum16': sum16,
    'djb2': djb2,
    'sdbm': sdbm,
    'fnv1a': fnv1a,
    'fnv1': fnv1,
    'jenkins': jenkins,
}

TARGETS = {0x1896, 0x1EEE}
print('=== 候选 tag 在各算法下的 16 位 hash ===')
for name, fn in ALGOS.items():
    hits = []
    for c in CAND:
        for enc in (c.encode(), c.lower().encode(), c.upper().encode()):
            h = fn(enc)
            if h in TARGETS:
                hits.append((c, enc, h))
    if hits:
        print('  %-14s ★命中 %s' % (name, hits))
    else:
        print('  %-14s 无' % name)

print()
print('=== 看看各算法对已知 tag 的输出（找规律用）===')
for c in CAND[:6]:
    print('  %-22s ' % c, {n: '%04X' % fn(c.encode()) for n, fn in ALGOS.items()})