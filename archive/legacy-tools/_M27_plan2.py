# -*- coding: utf-8 -*-
# 生成「位」的替换清单（修「们」的前置步骤）
# 目标：把全部 137 处「位」换成同义字，腾出第357格给「们」
import sys, struct, re, json
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

# 替换规则：按词组优先级（长词优先）
RULES = [
    ("排位赛", "排名赛"), ("排位）", "排名）"), ("排位，", "排名，"),
    ("段位", "等级"),
    ("就位了", "到位了"), ("就位，", "到位，"), ("就位。", "到位。"),
    ("条位于", "条在"), ("位于", "在"),
    ("各位", "大家"),
    ("槽位", "槽号"),
    ("位置", "地点"),
    ("座位", "座"),
    ("几位", "几个"), ("一位", "一个"), ("有位", "有个"),
    ("这位", "这个"), ("那位", "那个"), ("哪位", "哪个"),
    ("站位", "地点"),
    ("就位", "到位"),
    ("空位", "空座"),
    ("驾驶位", "驾驶座"),
    ("位数", "个数"), ("位数", "名数"),
]


def fix_text(t):
    out = t
    for a, b in RULES:
        out = out.replace(a, b)
    return out


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    sl = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        sl.append(s)
    return id1, id2, sl, q


plan = []
leftover = []
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, sl, endp = rec(d, p)
        except Exception:
            continue
        t = "".join(B[s - 32] if 0 <= s - 32 < len(B) else "{%d}" % s for s in sl)
        if "位" not in t:
            continue
        nt = fix_text(t)
        plan.append(dict(file=name, id1="%04X" % a, id2="%04X" % b_,
                         old=t, new=nt, changed=nt != t,
                         rec_off=p, slots=sl, end=endp))
        if "位" in nt:
            leftover.append((name, "%04X.%04X" % (a, b_), t, nt))

print("含「位」记录 =", len(plan), " 其中被规则命中 =", sum(1 for r in plan if r["changed"]))
print("替换后仍含「位」 =", len(leftover))
print("\n=== 替换后仍含「位」的（需人工处理）===")
for name, ids, o, n in leftover:
    print("  %s [%s]\n    原: %s\n    新: %s" % (name, ids, o[:70], n[:70]))

print("\n=== 被规则命中的样本（前 15 条）===")
n = 0
for r in plan:
    if r["changed"]:
        print("  %s [%s.%s]" % (r["file"], r["id1"], r["id2"]))
        print("    原: %s" % r["old"][:66])
        print("    新: %s" % r["new"][:66])
        n += 1
        if n >= 15:
            break

json.dump([{k: v for k, v in r.items() if k in ("file", "id1", "id2", "old", "new", "changed")}
           for r in plan], open(r"F:/sr2-cn/_wei_plan.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n清单已存 F:/sr2-cn/_wei_plan.json")
