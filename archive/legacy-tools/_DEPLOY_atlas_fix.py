# -*- coding: utf-8 -*-
"""部署字体图集修复：textures.vpp_pc 的 fnt_chinese 换成汉化图集

用法（游戏必须已退出）：
    cd /f/sr2-cn
    ./.venv/Scripts/python.exe _DEPLOY_atlas_fix.py
"""
import os, sys, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = r"F:\sr2-cn\_backup_E\textures.patched_20261013_174215_to_be_rolled_back.vpp_pc"
DST = os.path.join(G, "textures.vpp_pc")
BAK = r"F:\sr2-cn\_backup_I\textures.before_atlas_fix_20261014.vpp_pc"
WANT = "1f1906bcdb60085d72c4577c70581b7a"

# 1) 检查游戏是否在运行
import subprocess
try:
    out = subprocess.run(["tasklist"], capture_output=True, text=True, errors="ignore").stdout.lower()
except Exception as e:
    out = ""
if "sr2_pc.exe" in out:
    print("!!! SR2_pc.exe 正在运行，请先完全退出游戏再执行本脚本 !!!")
    sys.exit(1)
print("游戏未运行 ✓")

# 2) 校验源文件
h = hashlib.md5(open(SRC, "rb").read()).hexdigest()
print("源文件 md5 = %s" % h)
assert h == WANT, "源文件 md5 不符，中止！"
print("源文件校验通过 ✓")

# 3) 备份当前 textures
if not os.path.exists(BAK):
    print("备份当前 textures.vpp_pc ...")
    shutil.copy2(DST, BAK)
print("备份: %s  md5=%s" % (BAK, hashlib.md5(open(BAK, "rb").read()).hexdigest()))

# 4) 部署
print("部署中（1.2 GB，请稍候）...")
shutil.copy2(SRC, DST)
h2 = hashlib.md5(open(DST, "rb").read()).hexdigest()
print("部署后 textures.vpp_pc md5 = %s" % h2)
assert h2 == WANT, "部署结果 md5 不符！"

# 5) 验证图集
v = Vpp(DST)
e = next(x for x in v.entries() if x['name'] == 'fnt_chinese')
b = v.read(e)
del v
ha = hashlib.md5(b).hexdigest()
print("textures 内 fnt_chinese md5 = %s  (期望 34034076…)" % ha)
print("条目数 = %d" % len(Vpp(DST).entries()))
assert ha.startswith("34034076"), "图集未替换成功！"
print()
print("=" * 56)
print(" 部署成功！textures.vpp_pc 的字体图集已换成汉化图集")
print("=" * 56)
