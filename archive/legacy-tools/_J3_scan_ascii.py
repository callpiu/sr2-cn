# -*- coding: utf-8 -*-
"""最可靠：直接扫描 static_CH 里的明文 UTF-16LE（ASCII 字符 + 高字节0），
以及用 charlist 对 >0xFF 的 unit 解码。
先扫 ASCII 明文，人工确认哪些是文本记录。
"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('static_CH', 'le_strings'))
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)
print('CL=%d' % len(CL.body))

# 扫描所有 "ASCII 明文 run"（形如 ?\x00?\x00）
runs = []
i = 0
n = len(raw)
while i < n - 4:
    # 检查是否是纯 ASCII 的 UTF-16
    if 0x20 <= raw[i] <= 0x7E and raw[i + 1] == 0 and raw[i + 2] != 0 and raw[i + 3] == 0:
        j = i
        chars = []
        while j < n - 1 and raw[j + 1] == 0 and 0x20 <= raw[j] <= 0x7E:
            chars.append(chr(raw[j]))
            j += 2
        if len(chars) >= 5:
            runs.append((i, ''.join(chars)))
        i = j
    else:
        i += 1
print('ASCII runs=%d' % len(runs))
for off, s in runs[:40]:
    print('   @%7d  %s' % (off, s[:70]))
