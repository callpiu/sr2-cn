# -*- coding: utf-8 -*-
"""在 DFEngine.dll 中搜索 exe 全局地址 0xE8C470 / 0x2528B2C / 0x2528B30 的引用。"""
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
raw = open(G + '/DFEngine.dll', 'rb').read()

for name, va in [('语言码 0xE8C470', 0xE8C470),
                 ('cc_list 0x2528B2C', 0x2528B2C),
                 ('cc_cnt 0x2528B30', 0x2528B30),
                 ('lang_tbl 0xDD1104', 0xDD1104),
                 ('fmt_charlist 0xE26070', 0xE26070)]:
    b = struct.pack('<I', va)
    refs = [m.start() for m in re.finditer(re.escape(b), raw)]
    print("%-24s 引用 %d 次: %s" % (name, len(refs), [hex(r) for r in refs[:8]]))

print()
# 搜 exe 里 charlist 相关函数地址
for name, va in [('loadcharlist 0x7F4430', 0x7F4430),
                 ('font_init 0x7F46A0', 0x7F46A0)]:
    b = struct.pack('<I', va)
    refs = [m.start() for m in re.finditer(re.escape(b), raw)]
    print("%-24s 引用 %d 次: %s" % (name, len(refs), [hex(r) for r in refs[:8]]))

print()
# 搜 DFEngine 里的 "CH" 附近上下文（0x339b 等位置）
for off in [0x339b, 0x33fba, 0x3412e, 0x350ad]:
    print("0x%X 附近: %r" % (off, raw[max(0, off - 24):off + 24]))
