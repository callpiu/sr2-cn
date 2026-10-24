# -*- coding: utf-8 -*-
# 方案A：搬字形。先算出每个乱码字的「目标格」及该格现装的字（被顶替者）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp
from collections import Counter

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5

S1 = "你的弟兄们需要你的保护"
D1 = "任璨偶巧们雄衡任璨伪该"
S2 = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
D2 = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"

pairs = list(zip(S1, D1)) + list(zip(S2, D2))
print("乱码字对（去重）:")
m = {}
for c, d in pairs:
    if c in bidx and d in bidx:
        E = bidx[d] - OFF
        m.setdefault(c, set()).add(E)
for c, Es in m.items():
    print("  %s -> E=%s" % (c, sorted(Es)))

# 全文本频次
cnt = Counter()
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d): continue
        q = p + 4; out = []
        while True:
            s, = struct.unpack_from(">H", d, q); q += 2
            if s == 0: break
            k = s - 32
            out.append(B[k] if 0 <= k < len(B) else "?")
        for ch in set("".join(out)):
            cnt[ch] += 1

print("\n=== 搬字形可行性（顶替字频次 <= 15 才做）===")
plan = []
for c, Es in sorted(m.items()):
    if len(Es) > 1:
        print("  %s 多个E=%s  -> 跳过（上下文相关）" % (c, sorted(Es)))
        continue
    E = list(Es)[0]
    if E == bidx[c] - OFF:
        print("  %s E=%d 已是正确格 -> 无需搬" % (c, E))
        continue
    victim = B[E + OFF] if E + OFF < len(B) else "?"
    vf = cnt.get(victim, 0)
    src = bidx[c] - OFF
    ok = vf <= 15
    print("  %s: 格%d(装%s,频次%d) <- 复制格%d   %s" % (
        c, E, victim, vf, src, "✓可搬" if ok else "✗顶替高频字"))
    if ok:
        plan.append((c, E, src, victim, vf))

print("\n可搬 %d 个字: %s" % (len(plan), " ".join(p[0] for p in plan)))
import json
json.dump([{"char": c, "dst": e, "src": s, "victim": v, "vfreq": vf} for c, e, s, v, vf in plan],
          open(r"F:/sr2-cn/_glyphmove.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("已存 _glyphmove.json")
