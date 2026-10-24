# -*- coding: utf-8 -*-
"""把修复后的 charlist_CH.txt 写回 patch.vpp_pc（append-and-repoint）。"""
import sys, shutil, hashlib, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH = G + r'\patch.vpp_pc'
payload = open('F:/sr2-cn/_fixed_charlist_CH.txt', 'rb').read()

print("修复版 charlist_CH: %d 字节" % len(payload))

v = Vpp(PATCH)
ent = v.find('charlist_CH', 'txt')
print("目标条目:", ent['idx'], ent['name'] + '.' + ent['ext'], "size=%d body=%d" % (ent['size'], ent['body']))
old = v.read(ent)
print("旧内容 %d 字节, 含 count=: %s" % (len(old), b'count=' in old))

v.replace_body_appended(ent, payload)
tmp = 'F:/sr2-cn/_patch_new.vpp_pc'
v.save(tmp)
print("已写出临时文件:", tmp, os.path.getsize(tmp))

# 验证：重新打开临时文件，读 charlist_CH
v2 = Vpp(tmp)
e2 = v2.find('charlist_CH', 'txt')
raw2 = v2.read(e2)
print("\n=== 验证临时文件 ===")
print("  新 size =", len(raw2))
print("  首行 =", raw2.split(b'\r\n')[0][:70])
print("  含 count= :", b'count=' in raw2[:400])
import re
m = re.search(rb'count=(\d+)', raw2)
print("  count =", m.group(1).decode() if m else "无")
# 其它条目是否完好
print("  vpp 条目总数 =", v2.num, " (原 =", v.num, ")")
for nm in ['static_CH', 'voice_script_CH', 'platform_pc_CH']:
    e = v2.find(nm, 'le_strings')
    print("    %-22s size=%d" % (nm, e['size'] if e else -1))
