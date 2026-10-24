# -*- coding: utf-8 -*-
"""查 0x7F5030(码点->字形) / 0x7F4FA0(字形->码点) / 0x7F4E30(校验) 的全部调用者。
用字节级 E8/E9 rel32 扫描。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
buf = open(PATH, "rb").read()

def off2va(o):
    for s in pe.sections:
        if s.PointerToRawData <= o < s.PointerToRawData + s.SizeOfRawData:
            return base + s.VirtualAddress + (o - s.PointerToRawData)
    return None

def callers(target):
    res = []
    for i in range(len(buf) - 5):
        if buf[i] in (0xE8, 0xE9):
            rel = struct.unpack_from("<i", buf, i + 1)[0]
            va = off2va(i)
            if va is None:
                continue
            if va + 5 + rel == target:
                res.append((va, "CALL" if buf[i] == 0xE8 else "JMP"))
    return res

for tgt, name in [(0x7F4E30, "validate(校验)"),
                  (0x7F4EE0, "glyph->cp"),
                  (0x7F4F20, "cp->glyph"),
                  (0x7F4F60, "compress_char cp->glyph"),
                  (0x7F4FA0, "glyph-str->cp-str"),
                  (0x7F5030, "cp-str->glyph-str (渲染主入口)"),
                  (0x7ED840, "legacy_cp_map"),
                  (0x7F444A, "loader")]:
    cs = callers(tgt)
    print("\n=== 0x%08X %s : %d 个调用者 ===" % (tgt, name, len(cs)))
    for va, t in cs:
        print("   0x%08X  %s" % (va, t))
