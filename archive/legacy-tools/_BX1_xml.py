# -*- coding: utf-8 -*-
import os, sys, re, difflib
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

def getproj(path):
    v = Vpp(path)
    e = v.find('sr2', 'vint_proj')
    return v.read(e)

off = getproj(r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc")
cur = getproj(r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc")

for tag, b in (("官方", off), ("游戏内", cur)):
    t = b.decode('utf-8', 'replace')
    print("=== %s  len=%d" % (tag, len(b)))
    print("   BOM:", b[:3] == b'\xef\xbb\xbf', " 开头:", repr(t[:40]))
    # XML 合法性
    try:
        root = ET.fromstring(t)
        print("   XML 解析: OK, root =", root.tag)
        fi = root.iter('font_info')
        n = 0
        for f in fi:
            n += 1
            print("      font_info: file=%s alias=%s overlay=%s" % (
                (f.findtext('filename') or '').strip(),
                (f.findtext('alias') or '').strip(),
                (f.findtext('filename_overlay') or '').strip()))
        print("   font_info 数 =", n)
    except Exception as ex:
        print("   !! XML 解析失败:", ex)

print("\n=== 逐行 diff ===")
a = off.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
b = cur.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
for line in difflib.unified_diff(a, b, '官方', '游戏内', lineterm='', n=1):
    print(line)
