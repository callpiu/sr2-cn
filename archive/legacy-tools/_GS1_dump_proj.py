# -*- coding: utf-8 -*-
"""只读：dump common.vpp_pc 中 sr2.vint_proj 的字体段落；并列出所有 sr2.* 条目。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "common.vpp_pc"))
ents = v.entries()

print("=== common.vpp_pc 中所有 sr2.* 条目 ===")
for e in ents:
    if e['name'].lower().startswith('sr2'):
        print("  ", e['name'] + ('.' + e['ext'] if e['ext'] else ''), e['size'])

# 找 vint_proj
for e in ents:
    nm = (e['name'] + ('.' + e['ext'] if e['ext'] else '')).lower()
    if nm == 'sr2.vint_proj':
        body = v.read(e)
        print("\n=== sr2.vint_proj 全长", len(body), "===")
        txt = body.decode('latin-1')
        # 只打印含 font 的行及其上下文
        lines = txt.split('\n')
        for i, ln in enumerate(lines):
            if 'font' in ln.lower() or 'thin' in ln.lower() or 'header' in ln.lower() or 'bodyital' in ln.lower() or 'debug' in ln.lower():
                print(f"{i:4d}| {ln.rstrip()}")
        break
