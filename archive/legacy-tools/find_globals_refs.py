# -*- coding: utf-8 -*-
"""找 HUD 路径上与 slot(索引) 相关的 -5 / +5 常数，以及字形索引分配逻辑。
依据：UV 公式 j = charlist索引 − 5，若 HUD 走的是 +5 偏移的另一套索引，就会出现整体位移。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile, struct

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
buf = open(PATH, "rb").read()

def va2off(va):
    for s in pe.sections:
        if base + s.VirtualAddress <= va < base + s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (va - base - s.VirtualAddress)
    return None

# 1) 找所有引用 charlist 全局的指令（E8/E9 rel32 反查调用者 + 直接 mov 引用）
# 直接扫描字节：mov reg,[0x2528b2c] = 8B 0D 2C 8B 52 02 等
GLOBALS = {0x2528B2C: "CHARLIST_PTR", 0x2528B30: "NUM_CCHARS", 0x2528B28: "FOREIGN_FLAG",
           0x2528B29: "FLAG29", 0x2528B34: "PTR2", 0x2528B38: "CNT2"}
prints = []
for va, name in GLOBALS.items():
    pat = struct.pack("<I", va)
    idx = 0
    hits = []
    while True:
        i = buf.find(pat, idx)
        if i < 0:
            break
        hits.append(i)
        idx = i + 1
    prints.append((name, va, hits))

for name, va, hits in prints:
    print("=== %s @ 0x%08X : %d 处字节引用 ===" % (name, va, len(hits)))
    for o in hits[:40]:
        # 把文件偏移转成 VA
        va_o = None
        for s in pe.sections:
            if s.PointerToRawData <= o < s.PointerToRawData + s.SizeOfRawData:
                va_o = base + s.VirtualAddress + (o - s.PointerToRawData)
                break
        print("   file_off 0x%08X  va 0x%08X  bytes=%s" % (o, va_o or 0, buf[o-6:o+6].hex()))
