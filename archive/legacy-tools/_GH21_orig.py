# -*- coding: utf-8 -*-
import sys, os, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

# 1) 原版 common 里的 vf3 N
p = r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/backup_original/common.vpp_pc"
print("读原版 common:", os.path.getsize(p))
v = Vpp(p)
for e in v.entries():
    nm = e["name"] or ""
    if nm.startswith(("fnt_", "jap", "ige_", "ug-debug")) and (e["ext"] or "") == "vf3_pc":
        raw = v.read(e)
        N = struct.unpack_from("<I", raw, 8)[0] if len(raw) >= 12 else -1
        print("   %-16s %8d B  N=%-6d md5=%s" % (nm, len(raw), N, hashlib.md5(raw).hexdigest()[:10]))
