# -*- coding: utf-8 -*-
# 直接裁出「引擎实际取用」的格子（E(c)），读出真实显示字
import sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, sheet

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


T2S = {"们": "們", "护": "護", "击": "擊", "谈": "談", "笔": "筆", "几": "幾", "袭": "襲"}


def E_of(ch):
    if ch in E_KNOWN:
        return E_KNOWN[ch], "known"
    t = T2S.get(ch, ch)
    if t in E_KNOWN:
        return E_KNOWN[t], "繁"
    if ord(t) not in CLV:
        return None, "缺"
    i = CLV.index(ord(t))
    return int(round(i + delta_at(i))), "插%d" % i


SENT2 = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
SENT1 = "你的弟兄们需要你的保护"

for tag, s in (("第1句", SENT1), ("第2句", SENT2)):
    print("\n=== %s : %s ===" % (tag, s))
    cells = []
    info = []
    for ch in s:
        e, how = E_of(ch)
        if e is None or e < 0 or e >= fc.N:
            cells.append([[0] * 34 for _ in range(34)])
            info.append("%s=?(E=%s,N=%d)" % (ch, e, fc.N))
            continue
        cells.append([[p[3] for p in row] for row in fc.cell(fc.atlas, e)])
        d = chr(CLC[e + 5]) if 0 <= e + 5 < len(CLC) else "?"
        info.append("%s(%d)->%s" % (ch, e, d))
    sheet(cells, r"F:/sr2-cn/_KS_%s.png" % tag, scale=3, cols=11)
    print("  " + " | ".join(info))
    print("  saved _KS_%s.png" % tag)
