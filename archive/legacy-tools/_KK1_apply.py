# -*- coding: utf-8 -*-
"""把修好的 patch.vpp_pc 装到游戏里（先备份原版）"""
import os, hashlib, shutil, subprocess

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
DST = os.path.join(G, "patch.vpp_pc")
SRC = r"F:/sr2-cn/_FIX/patch.vpp_pc"
BAKDIR = r"F:/sr2-cn/_backup_VANILLA"
BAK = os.path.join(BAKDIR, "patch.vpp_pc.vanilla_20261017")

WANT_SRC = "d94a153f490b94ea1fcdba0d32308186"   # 修好的 patch.vpp_pc
WANT_DST = "805ab98e85cccd90ef37ea525e2e461e"   # 原版 patch.vpp_pc

# 1) 游戏是否在运行
try:
    out = subprocess.run(["tasklist"], capture_output=True, text=True, errors="ignore").stdout.lower()
except Exception:
    out = ""
if "sr2_pc.exe" in out:
    print("!!! SR2_pc.exe 正在运行，请先完全退出游戏 !!!")
    raise SystemExit(1)
print("游戏未运行 ✓")

# 2) 校验源
h = hashlib.md5(open(SRC, "rb").read()).hexdigest()
print("修复版 md5 = %s" % h)
assert h == WANT_SRC, "修复版 md5 不符"
print("修复版校验通过 ✓")

# 3) 校验当前游戏文件
h0 = hashlib.md5(open(DST, "rb").read()).hexdigest()
print("当前 patch.vpp_pc md5 = %s" % h0)
assert h0 == WANT_DST, "当前游戏 patch.vpp_pc 不是预期的原版（md5 %s），中止！" % WANT_DST
print("当前文件校验通过 ✓（确认为原版）")

# 4) 备份
os.makedirs(BAKDIR, exist_ok=True)
if not os.path.exists(BAK):
    print("备份原版到 %s ..." % BAK)
    shutil.copy2(DST, BAK)
print("备份: %s  md5=%s" % (BAK, hashlib.md5(open(BAK, "rb").read()).hexdigest()))

# 5) 部署
print("部署中（48 MB）...")
shutil.copy2(SRC, DST)
h2 = hashlib.md5(open(DST, "rb").read()).hexdigest()
print("部署后 md5 = %s  %s" % (h2, "OK ✓" if h2 == WANT_SRC else "!!! 不符"))
print()
print("回退命令（如需要）：")
print('  cp "F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017" "%s"' % DST.replace("\\", "/"))
