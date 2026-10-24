# -*- coding: utf-8 -*-
"""最可靠的探针：原地把 REC1 的前 11 个槽位改成 ASCII 字母 A..K。

为什么这个设计能判别
    REC1 在干净文件里是 41 个槽位（含 [format] 标签）。
    文本后面有 00 00 终止符 + 对齐填充。
    我把前 11 个槽位写成 'A'..'K'，第 12 槽位写 00 00 终止 ——
    REC1 的新文本就变成 "ABCDEFGHIJK"（11 个 ASCII 字母）。
    ★ 原地写入，条目大小/偏移全不变，VPP 结构不动。

判别
    屏幕变成 ABCDEFGHIJK -> 字幕来自 REC1（问题在字形映射）
    仍是 11 个汉字乱码   -> 字母不可能渲染成汉字 -> 字幕不是 REC1

用法
    python probe_abc.py apply | restore | show
"""
import os, sys, struct, shutil, datetime, hashlib

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
CLEAN = os.path.join(G, "patch.vpp_pc.before_probe_rec2.bak")
H1 = 0x84F287ED
NEW = "ABCDEFGHIJK"


def find_rec(d, want):
    b, c, oa, offs = file_offsets(d)
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        if ((id1 << 16) | id2) == want:
            return off
    return None


def show():
    v = Vpp(PATH)
    cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    d = bytes(v.read(v.find("static_CH", "le_strings")))
    print("patch md5:", hashlib.md5(open(PATH, "rb").read()).hexdigest())
    off = find_rec(d, H1)
    if off is None:
        print("  ★ 找不到 REC1")
        return
    u, _ = read_units(d, off + 8)
    vals = [x for x, _ in u]
    print("  REC1 @%d  %d 槽位" % (off, len(vals)))
    print("       %r" % "".join(S.get(x, "·") for x in vals))
    print("       槽位: %s" % vals[:20])


def apply():
    if not os.path.exists(CLEAN):
        raise SystemExit("找不到干净基准: %s" % CLEAN)
    shutil.copy2(CLEAN, PATH)
    raw = bytearray(open(PATH, "rb").read())
    v = Vpp(PATH)
    cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    ent = v.find("static_CH", "le_strings")
    body = bytes(v.read(ent))
    pos = raw.find(body)
    if pos < 0:
        raise SystemExit("无法定位 static_CH")
    d = bytearray(body)
    off = find_rec(bytes(d), H1)
    if off is None:
        raise SystemExit("找不到 REC1")
    u, _ = read_units(bytes(d), off + 8)
    vals = [x for x, _ in u]
    print("REC1 @%d, %d 槽位" % (off, len(vals)))
    print("  原文本: %r" % "".join(S.get(x, "·") for x in vals))
    if len(vals) < len(NEW) + 1:
        raise SystemExit("槽位不够")
    for j, ch in enumerate(NEW):
        bp = off + 8 + j * 2
        s = ord(ch)
        d[bp] = (s >> 8) & 0xFF
        d[bp + 1] = s & 0xFF
    tb = off + 8 + len(NEW) * 2
    d[tb] = 0
    d[tb + 1] = 0
    for k in range(tb + 2, off + 8 + len(vals) * 2):
        d[k] = 0
    assert len(d) == ent["size"], (len(d), ent["size"])
    raw[pos:pos + len(d)] = d
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = PATH + ".v%s_before_abc.bak" % ts
    shutil.copy2(PATH, bak)
    open(PATH, "wb").write(bytes(raw))
    print("  新文本: %r" % NEW)
    print("备份:", os.path.basename(bak))
    print("新 md5:", hashlib.md5(bytes(raw)).hexdigest())
    print()
    show()


def restore():
    baks = sorted(f for f in os.listdir(G)
                  if f.startswith("patch.vpp_pc.v") and f.endswith("_before_abc.bak"))
    if not baks:
        print("无备份")
        return
    shutil.copy2(os.path.join(G, baks[-1]), PATH)
    print("已还原:", baks[-1])
    show()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    {"show": show, "apply": apply, "restore": restore}[cmd]()
