# -*- coding: utf-8 -*-
"""简体汉化版：计算 E(c) -> 显示字 -> 生成补丁（修正「几」，并做单调性检查）"""
import sys, re, json, os, bisect
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

VAN = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
fv = Font(VAN); CLV = fv.charlist
fc = Font(CN); CLC = fc.charlist

E_KNOWN = {"交": 282, "他": 296, "你": 331, "保": 349, "們": 357, "兄": 405, "免": 412,
           "到": 453, "去": 530, "受": 538, "弟": 962, "擊": 1216, "攻": 1238, "易": 1287,
           "正": 1453, "的": 1779, "要": 2263, "護": 2337, "進": 2486, "避": 2509, "需": 2651}
PTS = sorted((CLV.index(ord(c)), e - CLV.index(ord(c))) for c, e in E_KNOWN.items())


def delta_at(idx):
    if idx <= PTS[0][0]:
        return PTS[0][1]
    if idx >= PTS[-1][0]:
        return PTS[-1][1]
    for k in range(len(PTS) - 1):
        i0, d0 = PTS[k]; i1, d1 = PTS[k + 1]
        if i0 <= idx <= i1:
            return d0 + (d1 - d0) * ((idx - i0) / (i1 - i0) if i1 > i0 else 0)
    return 0


T2S = {"们": "們", "护": "護", "击": "擊", "谈": "談", "笔": "筆", "几": "幾", "袭": "襲",
       "进": "進", "这": "這", "车": "車", "没": "沒", "们": "們"}


def E_of(ch):
    """E(c) ≈ (原版 charlist 中码点小于 c 的个数) + Δ(该位置)"""
    if ch in E_KNOWN:
        return E_KNOWN[ch], "已知"
    pos = bisect.bisect_left(CLV, ord(ch))
    return int(round(pos + delta_at(pos))), "位置%d" % pos


SENTS = ["你的弟兄们需要你的保护", "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"]
pairs = []
seen = set()
log = []
for s in SENTS:
    for ch in s:
        if ch in seen:
            continue
        seen.add(ch)
        e, how = E_of(ch)
        if e is None or e < 0 or e + 5 >= len(CLC) or e >= fc.N:
            log.append("  %s : 跳过 (%s, E=%s)" % (ch, how, e))
            continue
        d = chr(CLC[e + 5])
        pairs.append([ch, d])
        log.append("  %s -> E=%-5d -> 显示 %s   [%s]  src格=%d dst格=%d" % (
            ch, e, d, how, CLC.index(ord(ch)) - 5 if ord(ch) in CLC else -1, e))

print("=== 对照表 ===")
print("\n".join(log))
print("\n=== 单调性检查（按码点排序的 E 应递增）===")
srt = sorted(((ord(c), c, d, E_of(c)[0]) for c, d in pairs))
bad = 0
for k in range(len(srt) - 1):
    if srt[k][3] is not None and srt[k + 1][3] is not None and srt[k][3] > srt[k + 1][3]:
        print("  ! 违反: %s(E=%d) > %s(E=%d)" % (srt[k][1], srt[k][3], srt[k + 1][1], srt[k + 1][3]))
        bad += 1
print("  违反 %d 处" % bad)

cfg = {"offset": 5, "pairs": pairs}
json.dump(cfg, open(r"F:/sr2-cn/pairs_cn.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已写入 pairs_cn.json（%d 对）" % len(pairs))
