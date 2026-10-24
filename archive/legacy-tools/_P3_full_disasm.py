# -*- coding: utf-8 -*-
"""完整反汇编 0x7F4430 (loadcharlist) 全函数，标注每一段。"""
import sys
import capstone
sys.path.insert(0, 'F:/sr2-cn')

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
raw = open(G + '/SR2_pc.exe', 'rb').read()
BASE = 0x400000
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = False

start, end = 0x3F4430, 0x3F46A0
for ins in md.disasm(raw[start:end], BASE + start):
    note = ""
    op = ins.op_str
    if '0xe260' in op:
        # 打印该地址处的字符串
        m = op.split('0x')[-1].split(']')[0].strip()
        try:
            fo = int(m, 16) - BASE
            s = raw[fo:raw.find(b'\x00', fo)]
            note = "  ; %r" % s
        except Exception:
            pass
    if '0xdd1104' in op:
        note = "  ; 语言码表"
    if '0xe8c470' in op:
        note = "  ; 语言码变量"
    if '0x2528b' in op:
        note = "  ; 字表全局"
    if '0xc97089' in op:
        note = "  ; ★ sscanf?"
    if '0xbf2c10' in op:
        note = "  ; sprintf?"
    if '0xc00db0' in op:
        note = "  ; malloc?"
    if '0x2770fe0' in op:
        note = "  ; 文件系统对象"
    print("0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, op, note))
