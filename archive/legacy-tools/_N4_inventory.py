# -*- coding: utf-8 -*-
"""盘点：要修的字幕需要哪些字符，已知多少映射，还缺多少。

已知映射
    pairs_cn.json      —— 简体版实测 19 对（用户读数）
    pairs_vanilla.json —— 原版实测 23 对（含繁体字）

两条目标字幕（简体汉化版文本）
    84F287ED: 你的弟兄们需要你的保护
    10AF1E62: 你的弟兄们要出去谈几笔生意，保护他们免遭袭击
"""
import re
import sys
import json

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

CN = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"

STR1 = "你的弟兄们需要你的保护"
STR2 = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"


def load_cl(p):
    v = Vpp(p)
    raw = v.read(v.find("charlist_CH", "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


cl = load_cl(CN)
IDX = {cp: i for i, cp in enumerate(cl)}

# 已知映射
known = {}
for f in (r"F:\sr2-cn\pairs_cn.json", r"F:\sr2-cn\pairs_vanilla.json"):
    cfg = json.load(open(f, encoding="utf-8"))
    for c, d in cfg["pairs"]:
        if c not in known:
            known[c] = d
        # 也允许繁体字作为键（因为字幕原文可能是繁体）
print("已知映射 %d 条:" % len(known))
print("  " + "  ".join("%s->%s" % (k, v) for k, v in sorted(known.items())))
print()

# 目标字符串需要的所有字符
need = set()
for s in (STR1, STR2):
    for ch in s:
        need.add(ch)
need.discard("　")
print("两条字幕共需 %d 个不同字符:" % len(need))
print("  " + "".join(sorted(need)))
print()

have = [c for c in sorted(need) if c in known]
miss = [c for c in sorted(need) if c not in known]
print("已有映射 (%d): %s" % (len(have), "".join(have)))
print("缺映射   (%d): %s" % (len(miss), "".join(miss)))
print()

# 缺的字符在 charlist 里的索引
print("缺映射字符的 charlist 索引:")
for c in miss:
    i = IDX.get(ord(c))
    print("  %-3s (U+%04X)  clist_idx=%-6s  目标格=%s" %
          (c, ord(c), i if i is not None else "不在表", (i - 5) if i is not None else "-"))
print()

# 另一条路线：直接用 pairs_cn.json 里的「显示字」替换原文
print("=" * 82)
print("路线 A：直接用已知映射替换（只覆盖已实测的字）")
print("=" * 82)
for name, s in (("字幕1", STR1), ("字幕2", STR2)):
    out = "".join(known.get(ch, ch) for ch in s)
    covered = sum(1 for ch in s if ch in known)
    print("  %s 原文: %s" % (name, s))
    print("       替换: %s" % out)
    print("       覆盖: %d/%d 字符" % (covered, len(s)))
    unknown = sorted(set(ch for ch in s if ch not in known))
    print("       未覆盖: %s" % "".join(unknown))
    print()

# 路线 B：因为 pairs_vanilla 是繁体字，检查原文的繁体对应
print("=" * 82)
print("路线 B：把简体原文转成繁体，再用 vanilla 映射（覆盖更多）")
print("=" * 82)
try:
    import opencc
    print("  opencc 可用")
except ImportError:
    print("  ★ 无 opencc，需手工提供简->繁对应")
    # 手工表（只针对需要的字）
    S2T = {
        "你": "你", "的": "的", "弟": "弟", "兄": "兄", "们": "們",
        "需": "需", "要": "要", "保": "保", "护": "護",
        "去": "去", "出": "出", "谈": "談", "几": "幾", "笔": "筆",
        "生": "生", "意": "意", "，": "，", "他": "他",
        "免": "免", "遭": "遭", "袭": "襲", "击": "擊",
        "正": "正", "进": "進", "行": "行", "交": "交", "易": "易",
        "避": "避", "受": "受", "到": "到", "攻": "攻",
    }
    va_map = json.load(open(r"F:\sr2-cn\pairs_vanilla.json", encoding="utf-8"))
    vmap = {c: d for c, d in va_map["pairs"]}
    for name, s in (("字幕1", STR1), ("字幕2", STR2)):
        trad = "".join(S2T.get(ch, ch) for ch in s)
        out = "".join(vmap.get(ch, ch) for ch in trad)
        cov = sum(1 for ch in trad if ch in vmap)
        print("  %s 简体: %s" % (name, s))
        print("       繁体: %s" % trad)
        print("       替换: %s" % out)
        print("       覆盖: %d/%d" % (cov, len(trad)))
        unk = sorted(set(ch for ch in trad if ch not in vmap))
        print("       未覆盖: %s" % "".join(unk))
        print()
