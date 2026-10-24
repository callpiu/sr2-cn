# -*- coding: utf-8 -*-
"""GL3(止损点 B 轮): 降级 —— 把 static_CH 里那两条记录 id 改成 0xFFFFFFFF。

依据：
  - 官方原版 static_CH 里根本没有 0xF284ED87 / 0xAF10621E 这两条 id，
    原版走英文回退（Mods/static_US.le_strings 里这两条 id 存在）⇒ 不会乱码
  - 记录格式：[id u32 大端][u16 大端 槽位...][0x0000 终止]
  - 只改 id、不动结构，最安全
"""
import sys, os, shutil, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK = r"F:\sr2-cn\_backup_P"
os.makedirs(BAK, exist_ok=True)
TARGETS = (0xF284ED87, 0xAF10621E)

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

pp = os.path.join(G, "patch.vpp_pc")
print("patch 改前: %d B  md5=%s" % (os.path.getsize(pp), md5f(pp)))
dst = os.path.join(BAK, "patch.vpp_pc.before_downgrade")
if not os.path.exists(dst):
    shutil.copy2(pp, dst)
    print("备份 ->", dst)

v = Vpp(pp)
for e in v.entries():
    if (e["name"] or "") == "static_CH":
        raw = bytearray(v.read(e))
        print("static_CH.%s %d B" % (e["ext"], len(raw)))
        for t in TARGETS:
            pat = struct.pack(">I", t)
            pos = raw.find(pat)
            print("  id 0x%08X @ %d" % (t, pos))
            assert pos > 0, t
            raw[pos:pos + 4] = b"\xFF\xFF\xFF\xFF"
        v.replace_body_appended(e, bytes(raw))
        v.save(pp)
print("patch 改后: %d B  md5=%s" % (os.path.getsize(pp), md5f(pp)))

# ---- 校验 ----
print("\n=== 校验 ===")
v2 = Vpp(pp)
for e in v2.entries():
    if (e["name"] or "") == "static_CH":
        raw = v2.read(e)
        for t in TARGETS:
            print("  id 0x%08X 仍在: %s" % (t, raw.find(struct.pack(">I", t)) >= 0))
        print("  0xFFFFFFFF 出现: %d 次" % raw.count(b"\xFF\xFF\xFF\xFF"))

# 确认英文回退源里这两条存在
print("\n=== Mods/static_US.le_strings 里确认 ===")
us = os.path.join(G, "Mods", "static_US.le_strings")
b = open(us, "rb").read()
for t in TARGETS:
    print("  id 0x%08X : %s" % (t, b.find(struct.pack(">I", t)) >= 0))
