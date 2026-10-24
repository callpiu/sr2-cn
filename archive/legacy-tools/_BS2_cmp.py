# -*- coding: utf-8 -*-
import os, sys, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

def getproj(path, tag):
    v = Vpp(path)
    e = v.find('sr2', 'vint_proj')
    if not e:
        print(tag, "no sr2.vint_proj"); return None
    b = v.read(e)
    print("%s  sr2.vint_proj size=%d md5=%s" % (tag, len(b), hashlib.md5(b).hexdigest()[:10]))
    return b

off = getproj(r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc", "官方  ")
cur = getproj(r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc", "游戏内")

def fonts(b, tag):
    t = b.decode('utf-8', 'replace')
    print("\n=== %s font_info ===" % tag)
    for m in re.finditer(r'<font_info>(.*?)</font_info>', t, re.S):
        blk = m.group(1)
        fn = re.search(r'<filename>(.*?)</filename>', blk)
        al = re.search(r'<alias>(.*?)</alias>', blk)
        ov = re.search(r'<filename_overlay>(.*?)</filename_overlay>', blk)
        print("   alias=%-20s file=%-18s overlay=%s" % (al.group(1) if al else '?',
              fn.group(1) if fn else '?', ov.group(1) if ov else '?'))

if off: fonts(off, "官方")
if cur: fonts(cur, "游戏内")

if off and cur:
    print("\n两版本相同?" , off == cur)
    if off != cur:
        # 找第一个差异
        n = min(len(off), len(cur))
        for i in range(n):
            if off[i] != cur[i]:
                print("首个差异 @", i)
                print("  官方:", off[max(0,i-80):i+120])
                print("  游戏:", cur[max(0,i-80):i+120])
                break
