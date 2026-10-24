# -*- coding: utf-8 -*-
# 决定性：反推 SR2 的字符串名 -> id 的 hash 算法
# 已知对：ACT_HELI_PROTECTION_HUD_TEXT -> 84F2.87ED
import sys, zlib, hashlib

NAME = b"ACT_HELI_PROTECTION_HUD_TEXT"
ID1, ID2 = 0x84F2, 0x87ED


def fnv1a32(b):
    h = 0x811C9DC5
    for c in b:
        h ^= c
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def fnv1_32(b):
    h = 0x811C9DC5
    for c in b:
        h = (h * 0x01000193) & 0xFFFFFFFF
        h ^= c
    return h


def djb2(b):
    h = 5381
    for c in b:
        h = ((h * 33) + c) & 0xFFFFFFFF
    return h


def djb2x(b):
    h = 5381
    for c in b:
        h = ((h * 33) ^ c) & 0xFFFFFFFF
    return h


def sdbm(b):
    h = 0
    for c in b:
        h = (c + (h << 6) + (h << 16) - h) & 0xFFFFFFFF
    return h


def jenkins(b):
    h = 0
    for c in b:
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= (h >> 6)
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= (h >> 11)
    h = (h + (h << 15)) & 0xFFFFFFFF
    return h


cands = {
    "crc32": zlib.crc32(NAME) & 0xFFFFFFFF,
    "crc32_inv": (~zlib.crc32(NAME)) & 0xFFFFFFFF,
    "fnv1a32": fnv1a32(NAME),
    "fnv1_32": fnv1_32(NAME),
    "djb2": djb2(NAME),
    "djb2x": djb2x(NAME),
    "sdbm": sdbm(NAME),
    "jenkins": jenkins(NAME),
}
for algo, v in cands.items():
    v2 = (v & 0xFFFF) | ((v >> 16) << 16)
    print("%-10s = 0x%08X   swap后=0x%04X.%04X   (目标 84F2.87ED)  %s" % (
        algo, v, v & 0xFFFF, v >> 16,
        "★命中" if v == 0x84F287ED or v == 0xED87F284 else ""))

# md5/sha1 前 4 字节
for algo in ("md5", "sha1", "sha256"):
    d = hashlib.new(algo, NAME).digest()
    v = int.from_bytes(d[:4], "little")
    print("%-10s = 0x%08X  %s" % (algo, v, "★" if v in (0x84F287ED, 0xED87F284) else ""))
