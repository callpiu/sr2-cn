# -*- coding: utf-8 -*-
"""决定性测试：改【面板活动名】记录，看面板是否变化。

候选记录
    @302268  hash 0x84C1140A  "…直升機突襲"        （活动名，17 槽位）
    @76240   hash 0x83335F42  "直昇機攻擊等級"       （7 槽位）
    @203738  hash 0x0F84271C  "直升機"              （3 槽位）
    @203540  hash 0x4B583B9C  "直升機"              （3 槽位）

做法
    把这几条的前几个槽位改成 ASCII（如 "AAAA"），原地等长覆盖。
    若面板出现 AAAA -> 面板走 static_CH；
    若面板不变     -> 面板也不走 static_CH（整个 CJK 路径另有来源）
"""
import os, sys, struct, shutil, datetime, hashlib, glob

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
BACKUP = r"F:\sr2-cn\_fontfix_backup"

TARGETS = {
    0x84C1140A: "PANEL-A",   # 直升機突襲（活动名）
    0x83335F42: "PANEL-B",   # 直昇機攻擊等級
    0x0F84271C: "PANEL-C",   # 直升機
    0x4B583B9C: "PANEL-D",   # 直升機
}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def get(off=None):
    v = Vpp(PATH)
    cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    d = bytes(v.read(v.find("static_CH", "le_strings")))
    b, c, oa, offs = file_offsets(d)
    res = {}
    for o in [x for x in dict.fromkeys(offs) if 0 < x <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, o)
        h = (id1 << 16) | id2
        if h in TARGETS:
            u, _ = read_units(d, o + 8)
            res[h] = (o, [x for x, _ in u], "".join(S.get(x, "·") for x, _ in u))
    return d, res


def show():
    print("patch md5: %s" % md5(PATH))
    d, res = get()
    for h in TARGETS:
        if h in res:
            o, slots, t = res[h]
            print("  0x%08X @%-8d len=%-4d %r" % (h, o, len(slots), t))
        else:
            print("  0x%08X 未找到" % h)


def apply():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(BACKUP, "patch.vpp_pc.before_panel_%s" % ts)
    shutil.copy2(PATH, bak)
    print("备份: %s" % os.path.basename(bak))

    raw = bytearray(open(PATH, "rb").read())
    v = Vpp(PATH)
    ent = v.find("static_CH", "le_strings")
    body = bytes(v.read(ent))
    pos = raw.find(body)
    d = bytearray(body)
    b, c, oa, offs = file_offsets(bytes(d))
    changed = 0
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        if h not in TARGETS:
            continue
        u, _ = read_units(bytes(d), off + 8)
        vals = [x for x, _ in u]
        new = TARGETS[h]
        if len(new) > len(vals):
            print("  %s 文本太长，跳过" % new)
            continue
        slots = [ord(ch) for ch in new] + [0x20] * (len(vals) - len(new))
        for j, s in enumerate(slots):
            bp = off + 8 + j * 2
            d[bp] = (s >> 8) & 0xFF
            d[bp + 1] = s & 0xFF
        print("  0x%08X -> %r" % (h, new))
        changed += 1
    assert len(d) == ent["size"]
    raw[pos:pos + len(d)] = d
    open(PATH, "wb").write(bytes(raw))
    print("修改 %d 条" % changed)
    print("新 md5: %s" % md5(PATH))
    print()
    show()
    print()
    print(">>> 进游戏看左上角【活动面板】")
    print("    若显示 PANEL-A / PANEL-B / ... -> 面板走 static_CH，我能继续修")
    print("    若面板完全没变                -> 面板文本也不来自 static_CH")


def restore():
    baks = sorted(glob.glob(os.path.join(BACKUP, "patch.vpp_pc.before_panel_*")))
    if not baks:
        print("无备份")
        return
    shutil.copy2(baks[-1], PATH)
    print("已还原: %s" % os.path.basename(baks[-1]))
    show()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    {"show": show, "apply": apply, "restore": restore}[cmd]()
