# -*- coding: utf-8 -*-
"""决定性探针：给字幕塞入「连续索引」的测试槽位，直接读出映射。

原理
    把 static_CH 里那条字幕记录改成【连续索引】的槽位序列：
        slot = 0x20 + k,  k = 100, 200, 300, ...
    然后把每个 k 对应的「字表字」写下来。
    截图后，屏幕上显示的字 与 字表字 对照，就能得到映射。
    因为每个位置的 k 都不同且跨度大，一次实验能覆盖很宽的范围。

为什么这次一定有效
    之前所有实验都是「换字」，观察者可能忽略细微差别；
    这次是【连续索引】—— 屏幕上会显示一串**完全陌生但可辨认**的字，
    且每个位置对应一个已知的 k，映射一目了然。

用法
    python probe_slots.py apply
    python probe_slots.py restore
    python probe_slots.py show
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
H2 = 0x10AF1E62

# 测试用索引（避开 ASCII 区，全部落在 CJK 区；间距 100 便于肉眼分辨）
TEST_IDX = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100,
            1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100,
            2200, 2300, 2400, 2500, 2600, 2700, 2800]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def get_charlist():
    v = Vpp(PATH)
    return [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
            if l.strip().isdigit()]


def find_rec():
    v = Vpp(PATH)
    d = bytes(v.read(v.find("static_CH", "le_strings")))
    b, c, oa, offs = file_offsets(d)
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        if ((id1 << 16) | id2) == H2:
            u, _ = read_units(d, off + 8)
            return off, [x for x, _ in u]
    return None, None


def show():
    cn = get_charlist()
    off, slots = find_rec()
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    print("patch md5: %s" % md5(PATH))
    print("REC2 @%s, %d 槽位" % (off, len(slots) if slots else 0))
    if slots:
        print("  内容: %r" % "".join(S.get(x, "·") for x in slots))


def apply():
    cn = get_charlist()
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    off, slots = find_rec()
    if off is None:
        raise SystemExit("找不到 REC2")
    n = len(slots)
    print("REC2 @%d, %d 槽位" % (off, n))
    print("  原内容: %r" % "".join(S.get(x, "·") for x in slots))

    # 构造新槽位：使用 TEST_IDX（取前 n 个），其余用空格补齐
    use = TEST_IDX[:n]
    new_slots = [k + 0x20 for k in use] + [0x20] * (n - len(use))
    print()
    print("  测试索引 %d 个: %s" % (len(use), use))
    print("  对应字表字:")
    for k in use:
        print("     索引 %-5d -> %s (U+%04X)" % (k, S.get(k + 0x20, "?"), cn[k] if k < len(cn) else 0))

    # 原地写入（保持长度不变）
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(BACKUP, "patch.vpp_pc.before_slots_%s" % ts)
    shutil.copy2(PATH, bak)
    print()
    print("备份: %s" % os.path.basename(bak))

    raw = bytearray(open(PATH, "rb").read())
    v = Vpp(PATH)
    ent = v.find("static_CH", "le_strings")
    body = bytes(v.read(ent))
    pos = raw.find(body)
    if pos < 0:
        raise SystemExit("无法定位 static_CH")
    d = bytearray(body)
    for j, s in enumerate(new_slots):
        bp = off + 8 + j * 2
        d[bp] = (s >> 8) & 0xFF
        d[bp + 1] = s & 0xFF
    assert len(d) == ent["size"]
    raw[pos:pos + len(d)] = d
    open(PATH, "wb").write(bytes(raw))
    print("新 md5: %s" % md5(PATH))
    print()
    show()
    print()
    print(">>> 进游戏看直升机突击的字幕")
    print("    屏幕上会显示一串字；请按顺序把它们抄下来（或截图）")
    print("    我会与下面的表对照，得出 槽位->字形 的精确映射")
    print()
    print("=== 对照表（请按屏幕顺序核对）===")
    print("  %-6s %-8s %-8s %s" % ("位置", "槽位", "索引", "字表字"))
    for j, k in enumerate(use):
        print("  %-6d %-8d %-8d %s" % (j, k + 0x20, k, S.get(k + 0x20, "?")))


def restore():
    baks = sorted(glob.glob(os.path.join(BACKUP, "patch.vpp_pc.before_slots_*")))
    if not baks:
        print("无备份")
        return
    shutil.copy2(baks[-1], PATH)
    print("已还原: %s" % os.path.basename(baks[-1]))
    show()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    {"show": show, "apply": apply, "restore": restore}[cmd]()
