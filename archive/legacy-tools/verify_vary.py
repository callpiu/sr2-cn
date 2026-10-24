"""验证 probe_vary 重建后的 static_CH 是否完整。

背景
    probe_vary.py 把 REC1 改成「一二三」，但它【重建了整个 static_CH blob】。
    重建有风险：可能漏记录 / 桶表算错。
    本脚本对比【探针前】与【探针后】的 static_CH：
      - 记录数
      - 每条 hash + 文本
      - 差异清单
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CUR = os.path.join(G, "patch.vpp_pc")
BAK = os.path.join(G, "patch.vpp_pc.v20261012_154057_before_varyprobe.bak")


def dump(path, label):
    v = Vpp(path)
    cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
    ent = v.find("static_CH", "le_strings")
    d = bytes(v.read(ent))
    b, c, oa, offs = file_offsets(d)
    recs = {}
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 10):
            continue
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        p = off + 4
        vals = []
        while p + 1 < len(d):
            s = struct.unpack_from(">H", d, p)[0]
            if s == 0:
                break
            vals.append(s)
            p += 2
        recs[h] = "".join(S.get(x, "·") for x in vals)
    print("=== %s ===" % label)
    print("  static_CH 条目大小 %d, buckets=%d count=%d, 唯一 hash %d" %
          (ent["size"], b, c, len(recs)))
    return recs


a = dump(BAK, "探针前 (953CE862)")
b = dump(CUR, "探针后 (33EAE550)")
print()
print("=== 差异 ===")
only_a = set(a) - set(b)
only_b = set(b) - set(a)
print("  仅探针前有: %d 条" % len(only_a))
for h in list(only_a)[:10]:
    print("     0x%08X  %s" % (h, a[h][:50]))
print("  仅探针后有: %d 条" % len(only_b))
for h in list(only_b)[:10]:
    print("     0x%08X  %s" % (h, b[h][:50]))
diff = [h for h in set(a) & set(b) if a[h] != b[h]]
print("  内容不同: %d 条" % len(diff))
for h in diff[:10]:
    print("     0x%08X" % h)
    print("        前: %s" % a[h][:56])
    print("        后: %s" % b[h][:56])
