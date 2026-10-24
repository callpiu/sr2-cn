# -*- coding: utf-8 -*-
"""全 .text 段扫描：所有引用 0x2528B2C / 0x2528B30 / 0x2528B28 / 0x2528B29 的指令，
并定位所在函数边界（用 int3 填充 + call/ret 启发式）。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
buf = open(PATH, "rb").read()
text = [s for s in pe.sections if s.Name.startswith(b".text")][0]
tstart = base + text.VirtualAddress
tend = tstart + text.Misc_VirtualSize
code = buf[text.PointerToRawData:text.PointerToRawData + text.Misc_VirtualSize]

GLOBALS = {0x2528B2C: "CHARLIST_PTR", 0x2528B30: "NUM_CCHARS",
           0x2528B28: "flag_underscore", 0x2528B29: "flag_rare"}

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
insns = list(md.disasm(code, tstart))
print("total insns = %d" % len(insns))

refs = []
for idx, ins in enumerate(insns):
    line = ("%s %s" % (ins.mnemonic, ins.op_str))
    for g, name in GLOBALS.items():
        if ("0x%x" % g) in line:
            refs.append((ins.address, idx, name, line))
            break

print("\n=== 引用 charlist 全局的指令（共 %d 条）===" % len(refs))
for va, idx, name, line in refs:
    print("  0x%08X  [%-16s]  %s" % (va, name, line))

# 函数边界启发式：向上找最近的 int3/int3 填充 或 ret+填充
print("\n=== 每条引用所属函数起点（启发式）===")
def func_start(i):
    j = i
    while j > 0:
        prev = insns[j - 1]
        if prev.mnemonic in ("int3",):
            return insns[j].address
        j -= 1
    return insns[0].address

seen = set()
for va, idx, name, line in refs:
    fs = func_start(idx)
    if fs in seen: continue
    seen.add(fs)
    print("  函数 0x%08X   （含引用 %s）" % (fs, name))
