# -*- coding: utf-8 -*-
"""反汇编 DFEngine 关键函数：get_localization_from_hash / StartParsing 尾部（路径拼接）。
并在 rdata 里找 .cxt / Mods / Strings 等字符串常量。
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
data = open(P, "rb").read()
pe = pefile.PE(P)
RT = 0x5C640000


def bytes_rva(rva, n):
    o = pe.get_offset_from_rva(rva)
    return data[o:o + n]


def dis(rva, n, label, stop=400):
    v = RT + rva
    code = bytes_rva(rva, n)
    print("\n" + "=" * 72)
    print("--- %s RVA=0x%X VA=0x%08X ---" % (label, rva, v))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(code, v):
        print("  %08X: %-22s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
        if ins.mnemonic == "ret" and ins.address > v + stop:
            break


dis(0xAB370, 200, "MStrings::get_localization_from_hash")

# 在整份 DLL 里找字符串
print("\n=== 含 .cxt / Mods / Strings / static_ / voice_ 的字符串 ===")
import re
for m in re.finditer(rb"[ -~]{6,}", data):
    s = m.group().decode("ascii")
    if any(k in s for k in [".cxt", "Mods", "Strings", "static_", "voice_scripts", "juiced_", "platform_", "/", "\\"]) and len(s) < 80:
        if any(k in s for k in [".cxt", "Strings", "static_", "voice_", "juiced_", "platform_"]):
            print("  @0x%X  %r" % (m.start(), s))
