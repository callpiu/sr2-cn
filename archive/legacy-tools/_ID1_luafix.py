# -*- coding: utf-8 -*-
# 第11轮改动: 注释掉 hud_msg.lua 里的 font="thin_overlay"，改走默认字体
import os, sys, shutil, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G   = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK  = os.path.join(G, "patch.vpp_pc")
BK  = r"F:/sr2-cn/_backup_LUA"
os.makedirs(BK, exist_ok=True)

# 1) 备份
bp = os.path.join(BK, "patch.vpp_pc.before_luafont2")
if not os.path.exists(bp):
    shutil.copy2(PK, bp)
print("backup ->", bp, os.path.getsize(bp))

before_md5 = hashlib.md5(open(PK,'rb').read()).hexdigest()
print("before md5", before_md5, "size", os.path.getsize(PK))

# 2) 改
v = Vpp(PK)
e = v.find("hud_msg", "lua")
d = v.read(e)
OLD = b'vint_set_property(o, "font", "thin_overlay")'
NEW = b'--vint_set_property(o, "font", "thin_overlay")  --sr2cn: use default font'
cnt = d.count(OLD)
print("occurrences:", cnt)
assert cnt == 1, "预期恰好 1 处"
nd = d.replace(OLD, NEW)
print("lua size %d -> %d" % (len(d), len(nd)))
v.replace_body_appended(e, nd, align=0x800)
v.save(PK)

after_md5 = hashlib.md5(open(PK,'rb').read()).hexdigest()
print("after  md5", after_md5, "size", os.path.getsize(PK))

# 3) 回读校验
v2 = Vpp(PK)
d2 = v2.read(v2.find("hud_msg", "lua"))
print("verify NEW present:", NEW in d2, " OLD present:", OLD in d2)
print("verify size:", len(d2))
