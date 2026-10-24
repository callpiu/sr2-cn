# -*- coding: utf-8 -*-
"""部署 / 卸载 dinput8.dll 代理。"""
import os
import sys
import shutil
import hashlib
import datetime

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = r"F:\sr2-cn\asi\dinput8.dll"
DST = os.path.join(G, "dinput8.dll")
BAK = os.path.join(G, "dinput8.dll.sr2fix_backup")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def status():
    print("=== 部署状态 ===")
    if os.path.exists(DST):
        h = md5(DST)
        src = md5(SRC) if os.path.exists(SRC) else "?"
        print("  dinput8.dll 存在: %d 字节, md5 %s" % (os.path.getsize(DST), h[:16]))
        print("  %s" % ("✓ 是我们的代理" if h == src else "★ 不是我们的代理（其它来源）"))
    else:
        print("  dinput8.dll 不存在（未部署）")
    print("  源文件: %s (%s)" % (SRC, md5(SRC)[:16] if os.path.exists(SRC) else "缺失"))


def deploy():
    if not os.path.exists(SRC):
        print("★ 源文件不存在: %s" % SRC)
        return
    # 若已有非我们的 dinput8.dll，先备份
    if os.path.exists(DST):
        if md5(DST) == md5(SRC):
            print("已经是我们的代理，无需重复部署")
            status()
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        b = BAK + "." + ts
        shutil.copy2(DST, b)
        print("已备份原有 dinput8.dll -> %s" % os.path.basename(b))
    shutil.copy2(SRC, DST)
    print("已部署: %s -> %s" % (SRC, DST))
    print()
    status()
    print()
    print("=" * 62)
    print("  现在直接启动游戏（Steam 或 SR2_pc.exe）即可")
    print("  DebugView 里应能看到 [SR2FIX] 开头的输出")
    print("=" * 62)


def uninstall():
    if not os.path.exists(DST):
        print("未部署，无需卸载")
        return
    os.remove(DST)
    print("已删除 %s" % DST)
    # 恢复备份
    import glob
    bs = sorted(glob.glob(BAK + ".*"))
    if bs:
        shutil.copy2(bs[-1], DST)
        print("已恢复原 dinput8.dll <- %s" % os.path.basename(bs[-1]))
    print()
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "deploy": deploy, "uninstall": uninstall}.get(cmd, status)()
