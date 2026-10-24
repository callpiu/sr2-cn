# -*- coding: utf-8 -*-
"""分析 DFEngine.dll 如何解析 ForceLanguage，以及它如何设置引擎语言码 0xE8C470。
DFEngine ImageBase=0x10000000, .text VA=0x1000 RA=0x400
=> 文件偏移 = VA - 0x10000000 + 0x400 - 0x1000 = VA - 0x10000C00 + ... 需按节区算。
"""
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')
import pefile

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
path = G + '/DFEngine.dll'
raw = open(path, 'rb').read()
pe = pefile.PE(path, fast_load=True)
BASE = pe.OPTIONAL_HEADER.ImageBase
secs = []
for s in pe.sections:
    secs.append((s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData,
                 s.Name.rstrip(b'\x00').decode('latin1', 'replace')))

def va2fo(va):
    for va0, vs, ra, rs, nm in secs:
        if va0 <= va < va0 + max(vs, rs):
            return ra + (va - va0)
    return None

# 找 ForceLanguage 字符串的 VA
idx = raw.find(b'ForceLanguage')
fo = idx
# 反查 VA
def fo2va(fo):
    for va0, vs, ra, rs, nm in secs:
        if ra <= fo < ra + rs:
            return va0 + (fo - ra)
    return None

va = fo2va(fo)
print("'ForceLanguage' 文件偏移=0x%X  VA=0x%X" % (fo, va))
print("  字符串:", raw[fo:fo + 32])

# 搜索对该 VA 的引用（32位绝对地址）
b = struct.pack('<I', va)
refs = [m.start() for m in re.finditer(re.escape(b), raw)]
print("\n引用该 VA 的位置(文件偏移):", [hex(r) for r in refs])
for r in refs:
    rva = fo2va(r)
    print("  fo=0x%X va=0x%X  附近:", raw[max(0, r - 16):r + 16].hex(' ').upper())
