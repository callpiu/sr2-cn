# -*- coding: utf-8 -*-
# 决定性检验：B 是否近似按码点排序？乱序处是否就是乱码字？
# 字幕A 实证（用户读数 100% 可靠）：
#   你/的/兄/弟/需/要/保  7 个字引擎取格 = B.index(c)   -> 正确显示
#   們 -> 位    護 -> 该
# 假设：引擎表 M = 按 Unicode 码点排序的字符表；B = 原 charlist（近似码点序、少数乱序）
import sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
raw = f.v.read(f.cl_entry).decode("utf-8")
B = []
for L in raw.split("\r\n"):
    s = L.strip()
    if s.startswith("//") or not s or s.startswith("count="):
        continue
    for tok in s.split():
        if tok.isdigit():
            B.append(chr(int(tok)))
print("B 长度 =", len(B))

# 1. 非单调点
bad = [i for i in range(len(B) - 1) if ord(B[i]) >= ord(B[i + 1])]
print("\nB 中非单调点数 =", len(bad))
print("前 40 个:", bad[:40])

# 2. 关键字位置
for ch in "們護你的兄弟需要保位该任璨":
    if ch in B:
        print("  %s B序=%d 码点=U+%04X" % (ch, B.index(ch), ord(ch)))

# 3. 构造 M = 按码点排序（去重后保持）
M = sorted(set(B), key=ord)
print("\nM 长度（去重）= ", len(M))
mi = {c: i for i, c in enumerate(M)}
print("字符  B.index   M.index   差")
for ch in "你你兄弟需要保們護位该任璨偶巧雄衡伪":
    if ch in mi:
        print("  %s   %6d   %6d  %+5d" % (ch, B.index(ch), mi[ch], mi[ch] - B.index(ch)))

# 4. 整体吻合度：若 M 是引擎表，字幕A 的 9 个正确字应满足 M(c)==B.index(c)
ok = [c for c in "你的兄弟需要保" if mi[c] == B.index(c)]
print("\n9 个正确字中 M(c)==B.index(c) 的:", ok, " (%d/9)" % len(ok))
print("們: M=%d  引擎实测=362   -> %s" % (mi["們"], "吻合" if mi["們"] == 362 else "不吻合"))
print("護: M=%d  引擎实测=2342  -> %s" % (mi["護"], "吻合" if mi["護"] == 2342 else "不吻合"))

# 5. 有多少字满足 M(c)==B.index(c)
same = sum(1 for c in B if mi[c] == B.index(c))
print("\n全表 M(c)==B.index(c) 的字数 = %d / %d (%.1f%%)" % (same, len(B), 100.0 * same / len(B)))

# 6. 差异字的 B 位置分布（前 60）
diff = [(B.index(c), c, mi[c] - B.index(c)) for c in B if mi[c] != B.index(c)]
print("\n差异字数 =", len(diff))
print("前 60 个 (B序, 字, M-B):", diff[:60])
