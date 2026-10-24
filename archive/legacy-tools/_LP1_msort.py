# -*- coding: utf-8 -*-
# 决定性实验：引擎表 M 的排序规则是什么？
# 实测约束（源字 -> 引擎取格号）：
#   你->371  的->1836  兄->422  弟->1035  需->2667  要->2296  保->391  们->362  护->2342
# B（charlist_CH，按码点排序）在这些位置的值：
#   B[371]=你 B[1836]=的 B[422]=兄 B[1035]=弟 B[2667]=需 B[2296]=要 B[391]=保 B[332]=们 B[1190]=护
# => M 与 B 只在 们/位、护/该 附近不同
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
B = [chr(cp) for cp in f.charlist]
CON = {"你": 371, "的": 1836, "兄": 422, "弟": 1035, "需": 2667,
       "要": 2296, "保": 391, "们": 362, "护": 2342}

print("B 长度 =", len(B))
print("约束核对（B[c] 应等于 c）:")
for c, e in CON.items():
    print("  %s B.index=%d  引擎取格=%d  B[引擎格]=%s" % (c, B.index(c), e, B[e] if e < len(B) else "?"))


def score(M, tag):
    """M 是候选表，检验 M[CON[c]] == c"""
    hit = miss = 0
    bad = []
    for c, e in CON.items():
        if e < len(M) and M[e] == c:
            hit += 1
        else:
            miss += 1
            bad.append("%s:期望M[%d]=%s 实际=%s" % (c, e, c, M[e] if e < len(M) else "OOB"))
    print("  %-28s 命中 %d/%d" % (tag, hit, hit + miss))
    if bad:
        for b in bad[:6]:
            print("      ", b)
    return hit


print("\n=== 候选排序 ===")
score(B, "B 本身（按码点）")

# GBK 排序（简体）
try:
    gbk = sorted(B, key=lambda c: (c.encode("gbk"), c))
    score(gbk, "按 GBK 编码排序")
except Exception as ex:
    print("  GBK 失败:", ex)

# 笔画数排序：用「康熙/通用笔画」无数据，用码点在 Big5 中的位置代替
# Big5：简体字无对应码 -> 用繁体对应字。先试直接用 big5 codec（繁体字可编）
trad_map = {"们": "們", "护": "護", "这": "這", "来": "來", "车": "車",
            "东": "東", "开": "開", "进": "進", "击": "擊", "么": "麼",
            "该": "該", "保": "保", "你": "你", "的": "的", "兄": "兄",
            "弟": "弟", "需": "需", "要": "要", "位": "位"}
def big5key(c):
    t = trad_map.get(c, c)
    try:
        return (0, t.encode("big5"))
    except Exception:
        return (1, c.encode("utf-8"))
b5 = sorted(B, key=big5key)
score(b5, "按 Big5 排序(简->繁)")

# 反转
score(list(reversed(B)), "B 反转")

# 按「使用频率」无数据。试：按 UTF-16 高位优先（等同码点）
score(sorted(B, key=lambda c: ord(c)), "按码点(=B)")

# 关键：M 若按 Big5 排序，则 M[362]=们 意味着 们(們) 的 Big5 名次=362
print("\n=== 检验：们(們)/护(護) 的 Big5 名次 ===")
b5idx = {c: i for i, c in enumerate(b5)}
for c in "们护你兄弟需要保位该":
    t = trad_map.get(c, c)
    try:
        code = t.encode("big5").hex()
    except Exception:
        code = "N/A"
    print("  %s(繁%s) big5=%s  在b5表中名次=%s" % (c, t, code, b5idx.get(c, "?")))
