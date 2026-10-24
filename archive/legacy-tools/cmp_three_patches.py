"""对比三个 patch.vpp_pc：官方多语言版 vs 汉化版 vs 当前。

重点
    charlist_CH 的【项数】与【简/繁】特征
    fnt_chinese.vf3_pc 的字形数 N
    static_CH 里活动字幕记录的内容
"""
import os, sys, struct, hashlib

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
FILES = {
    "官方多语言(IdolNinja)": r"F:\sr2-cn\_tw_patch\patch.vpp_pc",
    "汉化版(第三方)": os.path.join(G, "patch.vpp_pc.v20261012_143820_before_ammo.bak"),
    "当前部署": os.path.join(G, "patch.vpp_pc"),
}
H1, H2 = 0x84F287ED, 0x10AF1E62
TESTS = {"会": 0x4F1A, "會": 0x6703, "楼": 0x697C, "樓": 0x6A13,
         "选": 0x9009, "選": 0x9078, "车": 0x8F66, "車": 0x8ECA}

for lab, p in FILES.items():
    if not os.path.exists(p):
        print("=== %s  不存在 ===" % lab)
        continue
    v = Vpp(p)
    print("=== %s ===" % lab)
    print("  %d 条目, %d 字节, md5 %s" %
          (v.num, os.path.getsize(p), hashlib.md5(open(p, 'rb').read()).hexdigest()[:16]))
    # charlist
    e = v.find("charlist_CH", "txt")
    if e:
        raw = v.read(e).decode("utf-8", "replace")
        cps = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
        print("  charlist_CH: %d 字节 -> %d 项" % (e["size"], len(cps)))
        marks = []
        for ch, cp in TESTS.items():
            marks.append("%s%s" % (ch, "✓" if cp in cps else "✗"))
        print("    简/繁特征: %s" % " ".join(marks))
    else:
        print("  charlist_CH: 无")
    # vf3
    e = v.find("fnt_chinese", "vf3_pc")
    if e:
        d = v.read(e)
        N, = struct.unpack_from("<i", d, 0x08)
        print("  fnt_chinese.vf3_pc: %d 字节, N=%d" % (e["size"], N))
    # g_peg
    e = v.find("fnt_chinese", "g_peg_pc")
    if e:
        print("  fnt_chinese.g_peg_pc: %d 字节" % e["size"])
    # 活动字幕记录
    e = v.find("static_CH", "le_strings")
    if e:
        d = bytes(v.read(e))
        cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
        S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
        b, c, oa, offs = file_offsets(d)
        found = 0
        for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
            id1, id2 = struct.unpack_from("<HH", d, off)
            h = (id1 << 16) | id2
            if h not in (H1, H2):
                continue
            u, _ = read_units(d, off + 8)
            t = "".join(S.get(x, "·") for x, _ in u)
            print("  static_CH 0x%08X: %s" % (h, t[:70]))
            found += 1
        if not found:
            # 用 US 字表解
            print("  static_CH: 无 0x84F287ED/0x10AF1E62 记录")
    print()
