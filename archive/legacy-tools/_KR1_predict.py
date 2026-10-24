# -*- coding: utf-8 -*-
# 用「E 构建无关 + E(简)=E(繁) + Δ 插值」预测汉化版两句的显示字，并与截图比对
import sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

VAN = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"

fv = Font(VAN)
CLV = fv.charlist
fc = Font(CN)
CLC = fc.charlist
print("charlist 原版=%d  汉化=%d" % (len(CLV), len(CLC)))

# 原版实测点：字 -> E(c)
E_KNOWN = {"交": 282, "他": 296, "你": 331, "保": 349, "們": 357, "兄": 405, "免": 412,
           "到": 453, "去": 530, "受": 538, "弟": 962, "擊": 1216, "攻": 1238, "易": 1287,
           "正": 1453, "的": 1779, "要": 2263, "護": 2337, "進": 2486, "避": 2509, "需": 2651}

# (索引, Δ=E-索引) 点，按索引排序
PTS = sorted((CLV.index(ord(c)), e - CLV.index(ord(c))) for c, e in E_KNOWN.items())
print("Δ 采样点:", [(i, d) for i, d in PTS])


def delta_at(idx):
    if idx <= PTS[0][0]:
        return PTS[0][1]
    if idx >= PTS[-1][0]:
        return PTS[-1][1]
    for k in range(len(PTS) - 1):
        i0, d0 = PTS[k]
        i1, d1 = PTS[k + 1]
        if i0 <= idx <= i1:
            if i1 == i0:
                return d0
            t = (idx - i0) / (i1 - i0)
            return d0 + (d1 - d0) * t
    return 0


# 简->繁 对照（只列需要的）
T2S = {"们": "們", "护": "護", "击": "擊", "谈": "談", "笔": "筆", "几": "幾", "袭": "襲",
       "进": "進", "这": "這", "们": "們"}


def trad(ch):
    return T2S.get(ch, ch)


def E_of(ch):
    if ch in E_KNOWN:
        return E_KNOWN[ch], "known"
    t = trad(ch)
    if t in E_KNOWN:
        return E_KNOWN[t], "via繁"
    if ord(t) not in CLV:
        return None, "繁形不在原版charlist"
    i = CLV.index(ord(t))
    return int(round(i + delta_at(i))), "插值(繁形索引%d)" % i


SENT1 = "你的弟兄们需要你的保护"
SENT2 = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
for tag, s in (("第1句", SENT1), ("第2句", SENT2)):
    out = []
    print("\n=== %s : %s ===" % (tag, s))
    for ch in s:
        e, how = E_of(ch)
        if e is None:
            out.append("?")
            print("   %s : 无法确定 (%s)" % (ch, how))
            continue
        d = chr(CLC[e + 5]) if 0 <= e + 5 < len(CLC) else "?"
        out.append(d)
        print("   %s -> E=%-5d -> 显示 %s   [%s]" % (ch, e, d, how))
    print("   预测显示: %s" % "".join(out))
