# -*- coding: utf-8 -*-
"""只读：对比官方多语言包 patch.vpp_pc 与汉化版 patch.vpp_pc 的条目清单。
重点：字体/字符集/vint/lua 相关文件是否不同。不做任何写入。"""
import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

OFF = r"F:\sr2-cn\pristine\patch.vpp_pc"
CN  = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"

def md5(b):
    return hashlib.md5(b).hexdigest()

def load(p):
    v = Vpp(p)
    ents = v.entries()
    d = {}
    for e in ents:
        key = (e['name'] + ('.' + e['ext'] if e['ext'] else ''))
        d[key.lower()] = e
    return v, d

vo, eo = load(OFF)
vc, ec = load(CN)
print("OFF entries =", len(eo), " size =", os.path.getsize(OFF))
print("CN  entries =", len(ec), " size =", os.path.getsize(CN))
print()

KEY = ('fnt', 'font', 'charlist', 'proj', 'vint', 'lua', 'jap', 'korea', 'chinese', 'ige')
print("=== 关键条目（名字含 fnt/font/charlist/proj/vint/lua/jap/korea/chinese/ige）===")
allk = sorted(set(eo) | set(ec))
for k in allk:
    if any(t in k for t in KEY):
        a = eo.get(k); b = ec.get(k)
        sa = a['size'] if a else None
        sb = b['size'] if b else None
        same = 'SAME' if (sa is not None and sa == sb) else 'DIFF'
        if a and b:
            ha = md5(vo.read(a)); hb = md5(vc.read(b))
            same = 'SAME' if ha == hb else 'DIFF(' + ha[:8] + '/' + hb[:8] + ')'
        print(f"{k:45s} off={str(sa):>9s} cn={str(sb):>9s}  {same}")

print()
print("=== 只在官方包中有的条目 ===")
for k in sorted(set(eo) - set(ec)):
    print("  OFF-ONLY:", k, eo[k]['size'])
print()
print("=== 只在汉化包中有的条目 ===")
for k in sorted(set(ec) - set(eo)):
    print("  CN-ONLY :", k, ec[k]['size'])
