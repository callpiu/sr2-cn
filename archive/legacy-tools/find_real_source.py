"""搜索所有含「弟兄们」槽位序列的文件 —— 找出游戏真正读取的那一份。

重要背景
    Juiced 的 debug.txt 里有这一行：
        [DLL] Creating cache directory data from ...\loose.txt
    说明 Juiced 会建立【松散文件缓存】。
    如果缓存里有一份旧的 static_CH.le_strings，游戏可能读缓存而不是 patch.vpp_pc。

本脚本用「槽位序列」而非哈希搜索，最可靠。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}


def seq(s):
    try:
        return b"".join(struct.pack(">H", IDX[c] + 0x20) for c in s)
    except KeyError:
        return None


targets = {}
for w in ("弟兄们", "需要你的保护", "要出去谈几笔生意", "他们免遭袭击"):
    q = seq(w)
    if q:
        targets[w] = q
        print("模式 %-14s %s" % (w, q.hex(" ")))
print()

print("=== 扫描全盘（含 Juiced 缓存目录）===")
n = 0
scanned = 0
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup", "reshade-shaders", "_vanilla_test", "_probe")):
        continue
    for f in fs:
        p = os.path.join(root, f)
        try:
            sz = os.path.getsize(p)
            if sz > 400 * 1024 * 1024 or sz < 16:
                continue
        except Exception:
            continue
        scanned += 1
        try:
            d = open(p, "rb").read()
        except Exception:
            continue
        for w, q in targets.items():
            i = d.find(q)
            if i >= 0:
                print("  ★ %-64s %-16s @0x%X" % (os.path.relpath(p, G), w, i))
                n += 1
                break
print()
print("扫描 %d 个文件，命中 %d 处" % (scanned, n))
