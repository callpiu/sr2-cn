"""穷尽搜索：所有 VPP 容器 + exe，找「弟兄们」等活动文本。

用户确认：字幕在【活动开始、过场动画结束进入操作时】出现 -> 是「活动开始提示」。

之前只搜了 patch.vpp_pc。本脚本用【轻量 VPP 读取】遍历所有 .vpp_pc。
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 从 patch.vpp_pc 取 charlist（这个文件不大，可以直接读）
import sys
sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}


def seq(s):
    out = b""
    for c in s:
        if c not in IDX:
            return None
        out += struct.pack(">H", IDX[c] + 0x20)
    return out


targets = {}
for w in ("弟兄们", "需要你的保护", "保护他们免遭袭击", "突击", "停靠"):
    q = seq(w)
    if q:
        targets[w] = q

print("目标模式:")
for w, q in targets.items():
    print("  %-16s %s" % (w, q.hex(" ")))
print()


def light_scan(path, max_entry=40 * 1024 * 1024):
    hits = []
    try:
        f = open(path, "rb")
    except Exception:
        return hits
    with f:
        head = f.read(0x800)
        if len(head) < 0x800:
            return hits
        names_off, = struct.unpack_from("<I", head, 0x10)
        n, = struct.unpack_from("<I", head, 0x18)
        if n <= 0 or n > 200000:
            return hits
        names_at = ((0x800 + names_off) & 0xFFFFF800) + 0x800
        ext_at = ((names_at + n * 32) & 0xFFFFF800) + 0x800
        f.seek(0x800)
        raw = f.read(n * 28)
        data_start = ((ext_at + n * 8) & 0xFFFFF800) + 0x800
        for i in range(n):
            if (i + 1) * 28 > len(raw):
                break
            nmoff, extoff, _, body, size, _, _ = struct.unpack_from("<IIiiiii", raw, i * 28)
            if size <= 0 or size > max_entry:
                continue
            try:
                f.seek(data_start + body)
                d = f.read(size)
            except Exception:
                continue
            for w, q in targets.items():
                j = d.find(q)
                if j >= 0:
                    hits.append((w, i, j))
    return hits


print("=== 扫描所有 VPP ===")
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"):
        continue
    p = os.path.join(G, fn)
    sz = os.path.getsize(p)
    h = light_scan(p)
    if h:
        print("  ★ %-22s (%6.0f MB) 命中 %d 处" % (fn, sz / 1048576, len(h)))
        for w, i, j in h[:6]:
            print("      条目 #%d  %s @0x%X" % (i, w, j))
    else:
        print("    %-22s (%6.0f MB) 无" % (fn, sz / 1048576))

print()
print("=== 扫描 exe / DLL ===")
for fn in ("SR2_pc.exe", "DFEngine.dll", "sr2_pc_unpatched.exe", "SR2_pc.exe.bak"):
    p = os.path.join(G, fn)
    if not os.path.exists(p):
        continue
    d = open(p, "rb").read()
    found = []
    for w, q in targets.items():
        j = d.find(q)
        if j >= 0:
            found.append("%s@0x%X" % (w, j))
    print("  %-24s %s" % (fn, ", ".join(found) if found else "无"))
