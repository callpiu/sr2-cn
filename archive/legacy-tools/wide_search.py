# -*- coding: utf-8 -*-
"""全目录搜索：中文 UTF-8 字节 / GBK 字节 / 槽位序列。
   目标：找出「延」「丈」「律」「三」这些字到底藏在哪个文件里。"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SKIP_DIR = {"crashdumps", "__pycache__"}

# 目标字
CHARS = "延丈律三辩师王护"
pats = {}
for ch in CHARS:
    b = ch.encode("utf-8")
    pats["UTF8:" + ch] = b
    pats["GBK:" + ch] = ch.encode("gbk")
# 关键三字/二字组合
for s in ["辩护", "三王", "丈王", "辩护律师", "辩护延师"]:
    pats["UTF8:" + s] = s.encode("utf-8")

# 槽位序列（大端 u16）
def seq(*v): return b"".join(int(x).to_bytes(2, "big") for x in v)
SLOTS = {
    "SEQ 辩 护 律 师":seq(2506, 1222, 1089, 1013),
    "SEQ 辩 护 延 师":   seq(2506, 1222, 1057, 1013),
    "SEQ 三 王":         seq(271, 1796),
    "SEQ 丈 王":         seq(270, 1796),
}
pats.update(SLOTS)

files, total, skipped = 0, 0, 0
for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIR]
    for f in fs:
        p = os.path.join(root, f)
        try:
            if os.path.getsize(p) > 200 * 1024 * 1024:
                skipped += 1; continue
            d = open(p, "rb").read()
        except Exception:
            skipped += 1; continue
        files += 1; total += len(d)
        hits = [k for k, v in pats.items() if v in d]
        if hits:
            rel = os.path.relpath(p, G)
            # 细分位置
            det = []
            for h in hits:
                i = d.find(pats[h])
                det.append("%s@0x%X" % (h, i))
            print("  %-58s %s" % (rel, "  ".join(det[:8])))
print("\n扫描 %d 个文件 / %.1f MB（跳过 %d 个）" % (files, total / 1048576.0, skipped))