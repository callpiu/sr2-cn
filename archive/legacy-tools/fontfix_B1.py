# -*- coding: utf-8 -*-
"""候选 B1：只改 common.vpp_pc 的 vf3 + pegs.vpp_pc 的描述符（不动 textures）。

原理
    字幕走别名 thin_overlay -> (fnt_body_n, fnt_body_s)。
    把这两个字体的「度量数据（vf3）」换成中文的（N=2838），
    并把 pegs 描述符改成与 fnt_chinese 一致。
    图集暂不动（仍是英文字体的图）—— 目的是先验证「改了有没有反应」。

安全设计
    ★ 全部用「原地等长覆盖」：
      - common.vpp_pc：把 fnt_chinese 的 vf3 前 7584 字节原地写进 fnt_body_n 的 vf3
        （N 字段从 224 改成 2838 需要更长空间；改用【写头部关键字段】的方式）
      - pegs.vpp_pc：把描述符的关键字段改成与 fnt_chinese 一致（等长，条目大小不变）
    ★ 不动容器结构、不动条目表、不动 size 字段 ⇒ 不会损坏 VPP

用法
    python fontfix_B1.py apply
    python fontfix_B1.py restore
    python fontfix_B1.py diff
"""
import os, sys, struct, shutil, datetime, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp, parse_vf3_header

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
TARGETS = ["fnt_body_n", "fnt_body_s"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def show_desc(path=os.path.join(G, "pegs.vpp_pc")):
    with LightVpp(path) as pv:
        for e in pv.entries():
            nm = pv.name(e)
            if nm in TARGETS + ["fnt_chinese"]:
                d = pv.read(e)
                i = d.find(b"fnt_")
                print("  %-14s len=%-3d 字段=%s  文件名=%r" %
                      (nm, len(d), d[:0x20].hex(" "), d[i:].rstrip(b"\x00").decode("latin1")))


def show_vf3(path=os.path.join(G, "common.vpp_pc")):
    with LightVpp(path) as cv:
        for e in cv.entries():
            nm = cv.name(e)
            if nm in TARGETS + ["fnt_chinese"] and cv.ext(e) == "vf3_pc":
                h = parse_vf3_header(cv.read(e))
                print("  %-14s size=%-6d N=%-5d W=%-3d H=%-3d RenderH=%-3d CharSpacing=%-4d KernPairs=%-4d" %
                      (nm, e["size"], h["N"], h["W"], h["H"], h["RenderH"], h["CharSpacing"], h["KernPairs"]))


def diff():
    print("=== pegs 描述符（当前）===")
    show_desc()
    print()
    print("=== common vf3（当前）===")
    show_vf3()
    print()
    print("=== 游戏目录文件 md5 ===")
    for f in ("common.vpp_pc", "pegs.vpp_pc"):
        p = os.path.join(G, f)
        print("  %-16s %s" % (f, md5(p)))


def apply_B1():
    """改 pegs 描述符（等长原地覆盖）。"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(G, "pegs.vpp_pc")
    bak = os.path.join(BACKUP, "pegs.vpp_pc.before_B1_%s" % ts)
    shutil.copy2(path, bak)
    print("备份: %s" % os.path.basename(bak))

    # 读 fnt_chinese 的描述符作为模板
    with LightVpp(path) as pv:
        tmpl = None
        recs = []
        for e in pv.entries():
            nm = pv.name(e)
            if nm == "fnt_chinese":
                tmpl = pv.read(e)
            if nm in TARGETS:
                recs.append((nm, e, pv.read(e)))
    if tmpl is None:
        raise SystemExit("找不到 fnt_chinese 描述符")
    print("模板 fnt_chinese 描述符 (%d 字节): %s" % (len(tmpl), tmpl[:0x20].hex(" ")))

    # 原地改写：只改「与 fnt_chinese 不同的字段」，文件名保持原样
    raw = bytearray(open(path, "rb").read())
    with LightVpp(path) as pv:
        data_start = pv.data_start
    CHANGED = []
    for nm, e, d in recs:
        off = data_start + e["body"]
        new = bytearray(d)
        # 只改判定为「尺寸/类型」的字段（依据字段对齐表）
        #  +0x0E  discriminator : 04/05 -> 40
        #  +0x1D, +0x1F : 02 -> 08            （网格/尺寸相关）
        #  +0x36 与 +0x0E 同（重复块）
        #  +0x08 (u32) : 描述符长度 -> 用模板的
        #  +0x20 (u16) : 91/92 -> 91
        for k in (0x0E, 0x1D, 0x1F, 0x36):
            new[k] = tmpl[k]
        struct.pack_into("<I", new, 0x08, struct.unpack_from("<I", tmpl, 0x08)[0])
        struct.pack_into("<H", new, 0x20, struct.unpack_from("<H", tmpl, 0x20)[0])
        CHANGED.append((nm, bytes(d), bytes(new)))
        raw[off:off + len(new)] = new

    open(path, "wb").write(bytes(raw))
    print()
    print("=== 已改写 ===")
    for nm, old, new in CHANGED:
        print("  %s:" % nm)
        print("     旧: %s" % old[:0x20].hex(" "))
        print("     新: %s" % new[:0x20].hex(" "))
    print()
    print("新 md5: %s" % md5(path))
    print()
    diff()


def restore():
    baks = sorted(f for f in os.listdir(BACKUP) if f.startswith("pegs.vpp_pc.before_B1_"))
    if not baks:
        print("无 B1 备份")
        return
    shutil.copy2(os.path.join(BACKUP, baks[-1]), os.path.join(G, "pegs.vpp_pc"))
    print("已还原: %s" % baks[-1])
    diff()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "diff"
    {"diff": diff, "apply": apply_B1, "restore": restore}[cmd]()
