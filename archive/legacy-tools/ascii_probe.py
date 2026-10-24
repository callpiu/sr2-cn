# -*- coding: utf-8 -*-
"""把 static_CH 里那两条字幕改成 ASCII 测试串，验证游戏是否真的读它。

如果屏幕出现 "ZZZTESTONE"，说明 static_CH 被读取（数据层有效）
如果还是乱码，说明字幕不来自 static_CH
"""
import os
import sys
import struct
import shutil
import datetime
import hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PATH = os.path.join(G, "patch.vpp_pc")
BACKUP = r"F:\sr2-cn\_fontfix_backup"
TARGETS = {0x84F287ED: "ZZZTESTONE", 0x10AF1E62: "ZZZTESTTWO"}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def apply():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(PATH, os.path.join(BACKUP, "patch.vpp_pc.before_ascii_%s" % ts))
    print("已备份")

    raw = bytearray(open(PATH, "rb").read())
    v = Vpp(PATH)
    ent = v.find("static_CH", "le_strings")
    body = bytes(v.read(ent))
    pos = raw.find(body)
    if pos < 0:
        raise SystemExit("无法定位 static_CH")
    d = bytearray(body)
    b, c, oa, offs = file_offsets(bytes(d))

    done = []
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        if h not in TARGETS:
            continue
        u, _ = read_units(bytes(d), off + 8)
        vals = [x for x, _ in u]
        txt = TARGETS[h]
        new = [ord(ch) for ch in txt] + [0x20] * (len(vals) - len(txt))
        for j, s in enumerate(new):
            bp = off + 8 + j * 2
            d[bp] = (s >> 8) & 0xFF
            d[bp + 1] = s & 0xFF
        done.append((h, txt, len(vals)))
        print("  0x%08X -> %r (%d 槽位)" % (h, txt, len(vals)))

    assert len(d) == ent["size"]
    raw[pos:pos + len(d)] = d
    open(PATH, "wb").write(bytes(raw))
    print("新 md5: %s" % md5(PATH))

    # 验证
    v2 = Vpp(PATH)
    cn = [int(l) for l in v2.read(v2.find("charlist_CH", "txt")).decode("utf-8").split("\n")
          if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
    b2, c2, oa2, offs2 = file_offsets(d2)
    print()
    print("=== 验证 ===")
    for off in [o for o in dict.fromkeys(offs2) if 0 < o <= len(d2) - 10]:
        id1, id2 = struct.unpack_from("<HH", d2, off)
        h = (id1 << 16) | id2
        if h in TARGETS:
            u, _ = read_units(d2, off + 8)
            print("  0x%08X = %r" % (h, "".join(S.get(x, "·") for x, _ in u)))


def restore():
    import glob
    bs = sorted(glob.glob(os.path.join(BACKUP, "patch.vpp_pc.before_ascii_*")))
    if not bs:
        print("无备份")
        return
    shutil.copy2(bs[-1], PATH)
    print("已还原 <- %s" % os.path.basename(bs[-1]))
    print("md5: %s" % md5(PATH))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "apply"
    {"apply": apply, "restore": restore}[cmd]()
