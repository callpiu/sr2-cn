# -*- coding: utf-8 -*-
"""读取 SR2_pc.exe 中字体初始化函数引用的所有字符串 / 常量"""
import struct, sys
sys.path.insert(0, r'F:\sr2-cn')
from _dis import PE

pe = PE(r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe")

def cstr(va, maxlen=64):
    off = pe.va2off(va)
    if off is None:
        return '<no va>'
    e = pe.d.find(b'\x00', off, off + maxlen)
    return pe.d[off:e].decode('latin1')

def f32(va):
    off = pe.va2off(va)
    if off is None:
        return None
    return struct.unpack_from('<f', pe.d, off)[0]

print("=== 字体名字符串 ===")
for va in (0xDE0FCC, 0xDE0FD0, 0xDE0FDC, 0xDE0FE8, 0xDE0FF0, 0xDE0FFC,
           0xDE1008, 0xDE1014, 0xDE1024, 0xDE1034, 0xDE1040, 0xDE104C,
           0xDE1058, 0xDE1060, 0xDE1068, 0xDE1078, 0xDE1084, 0xDE1098,
           0xDE10AC):
    print("  0x%08X  %r" % (va, cstr(va)))

print("=== charlist 相关 ===")
for va in (0xE26070, 0xE26080, 0xE2608C, 0xE26060, 0xE26090):
    print("  0x%08X  %r" % (va, cstr(va)))

print("=== 缩放常量 (float) ===")
for va in (0xE87628, 0xE5D840, 0xEDB664, 0xE5D83C, 0xE5D838, 0xDD09C4, 0xDD518C):
    print("  0x%08X  %r" % (va, f32(va)))

print("=== 语言表 0xDD1104 附近 ===")
off = pe.va2off(0xDD10C0)
seg = pe.d[off:off+0x140]
# 打印可见字符串
import re
for m in re.finditer(rb'[ -~]{2,}', seg):
    print("  0x%08X  %r" % (0xDD10C0 + m.start(), m.group().decode('latin1')))

print("=== 引用 0x252A5C8 的指令 ===")
for va in pe.find_imm_refs(0x252A5C8):
    print("  0x%08X" % va)
print("=== 引用 0xE98A24 的指令 ===")
for va in pe.find_imm_refs(0xE98A24):
    print("  0x%08X" % va)
print("=== 引用 0xE98A68 的指令 ===")
for va in pe.find_imm_refs(0xE98A68):
    print("  0x%08X" % va)
