# -*- coding: utf-8 -*-
# 评估修复代价：位/该 在字幕中的出现频率；以及 E(位)/E(该) 是否也是 357/2337
# 若 E(位)==357 则改第357格会顶坏「位」；若 E(位)==362 则可安全改
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5   # 图集第 k 格 = charlist[k+5]

# 用户实测的引擎取格：E(们)=357  E(护)=2337
# 正常应为 B.index(c)-OFF
print("=== 引擎取格实测 vs 应有值 ===")
for c, E in (("们", 357), ("护", 2337)):
    print("  %s: B序=%d  应有取格=%d  实测取格=%d  多偏移=%+d" % (
        c, bidx[c], bidx[c] - OFF, E, E - (bidx[c] - OFF)))

# 位/该 的应有取格
print("\n=== 位/该 的取格（若引擎正常，应为 B序-5）===")
for c in "位该":
    print("  %s: B序=%d  应有取格=%d" % (c, bidx[c], bidx[c] - OFF))

# 统计 位/该 在全部字幕中的出现次数
def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


cnt = {"位": 0, "该": 0, "们": 0, "护": 0}
samples = {"位": [], "该": []}
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        for ch in cnt:
            if ch in t:
                cnt[ch] += t.count(ch)
                if len(samples.get(ch, [])) < 5 and ch in "位该":
                    samples[ch].append((a, b_, t))
print("\n=== 四字在全部字幕中的出现次数 ===")
for ch, n in cnt.items():
    print("  %s: %d 次" % (ch, n))

print("\n=== 含「位」的字幕样本 ===")
for a, b_, t in samples["位"]:
    print("  [%04X.%04X] %s" % (a, b_, t[:70]))
print("\n=== 含「该」的字幕样本 ===")
for a, b_, t in samples["该"]:
    print("  [%04X.%04X] %s" % (a, b_, t[:70]))

# 关键：引擎表异常的字还有哪些？
# 思路：正常字 E = B序-5。若某字被报告乱码，其 E 异常。
# 目前只有 们/护 两组实测。要发现更多，需要用户报更多乱码。
print("\n=== 图集第 357 / 2337 格实际字形（读图已确认）===")
print("  第357格 = B[362] =", B[362], "  第2337格 = B[2342] =", B[2342])
