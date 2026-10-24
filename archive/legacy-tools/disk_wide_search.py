# -*- coding: utf-8 -*-
"""搜索乱码串/正确串的 UTF-16 宽字符形式（LE/BE，连续字符，非锚点数组）。
若命中某文件 → HUD 文本源是数据文件（本地化工具转换错误烧进数据）。
同时带正对照：正确串的宽形式 + slot 形式。"""
import sys, os
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def w(s, en):
    return s.encode("utf-16-le" if en == "LE" else "utf-16-be")

PATS = []
for en in ("LE", "BE"):
    PATS.append(("乱码全12_%s" % en, w("任璨偶巧位雄衡任璨伪该", en)))
    PATS.append(("乱码前5_%s" % en, w("任璨偶巧位", en)))
    PATS.append(("乱码前3_%s" % en, w("任璨偶", en)))
    PATS.append(("正确全12_%s" % en, w("你的弟兄们需要你的保护", en)))
    PATS.append(("正确前5_%s" % en, w("你的弟兄们", en)))

files = []
for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in ("directx", "microsoft.vc80.crt")]
    for f in fs:
        p = os.path.join(root, f)
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz >= 1024:
            files.append((p, sz))
files.sort(key=lambda x: -x[1])
print("搜索 %d 个文件..." % len(files))

CH = 48 * 1024 * 1024
OV = 1 << 16
hits = {n: [] for n, _ in PATS}
for p, sz in files:
    lb = os.path.relpath(p, G)
    big = sz > 150 * 1024 * 1024
    try:
        if big:
            with open(p, "rb") as f:
                base, prev = 0, b""
                while True:
                    blk = f.read(CH)
                    if not blk:
                        break
                    buf = prev + blk
                    b0 = base - len(prev)
                    for n, pat in PATS:
                        st = 0
                        while True:
                            i = buf.find(pat, st)
                            if i < 0:
                                break
                            hits[n].append((lb, b0 + i))
                            st = i + 1
                    prev = buf[-OV:]
                    base += len(blk)
        else:
            buf = open(p, "rb").read()
            for n, pat in PATS:
                st = 0
                while True:
                    i = buf.find(pat, st)
                    if i < 0:
                        break
                    hits[n].append((lb, i))
                    st = i + 1
    except Exception as ex:
        print("  %s 失败: %s" % (lb, ex))

print("\n=== 结果 ===")
for n, _ in PATS:
    v = hits[n]
    print("【%s】%d 处" % (n, len(v)))
    for x in v[:12]:
        print("     ", x)
