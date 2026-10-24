# -*- coding: utf-8 -*-
"""字体修复：一键状态查看 / 应用 / 回滚。

产物（当前已应用）
    common.vpp_pc : fnt_body_n / fnt_body_s 的 vf3_pc 换成中文字形度量 (N=2838)
    pegs.vpp_pc   : fnt_body_n / fnt_body_s 的描述符换成中文规格 (0x40/08/08)
    textures.vpp_pc / patch.vpp_pc : 未修改

用法
    python fontfix_status.py status     # 看当前状态
    python fontfix_status.py restore    # 回滚到官方原版
    python fontfix_status.py apply      # 重新应用（在回滚后使用）
"""
import os, sys, struct, shutil, hashlib, glob

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
REF_MD5 = {
    "common.vpp_pc": "f041934f15f06c6facc97d00e1ab7efd",
    "pegs.vpp_pc": "957e6cae5291a5cd8ea335801c85562d",
    "textures.vpp_pc": "fd6bb80a83b08bdf7e09720120f1966d",
    "patch.vpp_pc": "805ab98e85cccd90ef37ea525e2e461e",
}
FIXED_MD5 = {
    "common.vpp_pc": "b16ce2191fb184ffbaa0e49040e64118",
    "pegs.vpp_pc": "68e79a8d3a0b59130903536ad7e630b8",
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def status():
    print("=== 游戏目录文件状态 ===")
    for f, ref in REF_MD5.items():
        p = os.path.join(G, f)
        if not os.path.exists(p):
            print("  %-18s ★ 不存在" % f)
            continue
        h = md5(p)
        if h == ref:
            tag = "官方原版"
        elif h == FIXED_MD5.get(f):
            tag = "★ 已应用字体修复"
        else:
            tag = "其它（已修改）"
        print("  %-18s %12d  %s  %s" % (f, os.path.getsize(p), h[:16], tag))
    print()
    print("=== 字体条目实际内容 ===")
    print("  common.vpp_pc:")
    with LightVpp(os.path.join(G, "common.vpp_pc")) as v:
        for e in v.entries():
            nm = v.name(e)
            if nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese") and v.ext(e) == "vf3_pc":
                d = v.read(e)
                N, = struct.unpack_from("<i", d, 0x08)
                print("    %-14s size=%-6d N=%-5d %s" %
                      (nm, e["size"], N, "★ 中文" if N == 2838 else "ASCII"))
    print("  pegs.vpp_pc:")
    with LightVpp(os.path.join(G, "pegs.vpp_pc")) as v:
        for e in v.entries():
            nm = v.name(e)
            if nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese"):
                d = v.read(e)
                i = d.find(b"fnt_")
                print("    %-14s size=%-3d 字段=%s 文件=%s" %
                      (nm, e["size"], d[0x0C:0x20].hex(" "),
                       d[i:].rstrip(b"\x00").decode("latin1")))


def restore():
    print("=== 回滚到官方原版 ===")
    n = 0
    for f in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc", "patch.vpp_pc"):
        baks = sorted(glob.glob(os.path.join(BACKUP, f + ".before_*")))
        if not baks:
            # 也用固定备份
            baks = sorted(glob.glob(os.path.join(BACKUP, f)))
        if not baks:
            print("  %-18s 无备份，跳过" % f)
            continue
        src = baks[0]
        shutil.copy2(src, os.path.join(G, f))
        print("  %-18s <- %s" % (f, os.path.basename(src)))
        n += 1
    print("  已还原 %d 个文件" % n)
    print()
    status()


def apply_fix():
    # 先回滚到原版
    for f in ("common.vpp_pc", "pegs.vpp_pc"):
        baks = sorted(glob.glob(os.path.join(BACKUP, f + ".before_*")))
        if baks:
            shutil.copy2(baks[0], os.path.join(G, f))
    print("已重置为原版，正在应用修复...")
    os.system('"%s" "%s" apply' % (sys.executable, r"F:\sr2-cn\fontfix_Bfull.py"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "restore": restore, "apply": apply_fix}[cmd]()
