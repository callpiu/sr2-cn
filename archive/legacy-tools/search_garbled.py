"""决定性搜索：乱码字「任璨偶巧位雄衡」到底存在哪里？

思路
    不做 hash 假设。直接把用户看到的乱码字按【各种可能的编码】去全盘搜：
      - UTF-16LE / UTF-16BE（游戏内部宽字符串）
      - 槽位序列（大端 u16，charlist_CH 的 slot 值）
      - GBK / UTF-8

    如果找到，就说明屏幕用的是那个来源，而不是我们改的 static_CH 记录。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
USER1 = "任璨偶巧位雄衡任璨伪该"
USER2 = "任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮"
WANT1 = "弟兄们需要你的保护"
WANT2 = "弟兄们要出去谈几笔生意，保护他们免遭袭击"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}


def pats(s):
    out = {}
    out["utf16le"] = s.encode("utf-16-le")
    out["utf16be"] = s.encode("utf-16-be")
    out["gbk"] = s.encode("gbk", "ignore")
    out["utf8"] = s.encode("utf-8")
    # 槽位序列（大端）
    try:
        out["slot_be"] = b"".join(struct.pack(">H", IDX[c] + 0x20) for c in s)
        out["slot_le"] = b"".join(struct.pack("<H", IDX[c] + 0x20) for c in s)
    except KeyError:
        pass
    # 索引序列
    try:
        out["cpidx_be"] = b"".join(struct.pack(">H", IDX[c]) for c in s)
    except KeyError:
        pass
    return out


print("=== 目标模式 ===")
for name, s in (("乱码1", USER1), ("乱码2", USER2), ("应为1", WANT1), ("应为2", WANT2)):
    p = pats(s)
    print("  %s %r" % (name, s[:20]))
    for k, b in p.items():
        if len(b) >= 8:
            print("      %-8s %s" % (k, b[:32].hex(" ")))
print()

# 全盘搜索
files = []
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup", "reshade-shaders", "_vanilla_test", "_probe", "Juiced\\logs", "CrashDumps")):
        continue
    for f in fs:
        p = os.path.join(root, f)
        try:
            sz = os.path.getsize(p)
            if sz > 200 * 1024 * 1024 or sz < 16:
                continue
        except Exception:
            continue
        files.append(p)
print("扫描 %d 个文件..." % len(files))

targets = {}
for name, s in (("乱码1", USER1), ("乱码2", USER2)):
    for k, b in pats(s).items():
        if len(b) >= 8:
            targets["%s/%s" % (name, k)] = b

hits = 0
for p in files:
    try:
        d = open(p, "rb").read()
    except Exception:
        continue
    for name, b in targets.items():
        i = d.find(b)
        if i >= 0:
            print("  ★ %-58s %-18s @0x%X" % (os.path.relpath(p, G), name, i))
            hits += 1
print()
print("命中 %d 处" % hits)
