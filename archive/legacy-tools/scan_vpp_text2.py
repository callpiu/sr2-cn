"""穷尽搜索（修正版）：所有 VPP 容器 + exe，找活动文本。

sr2lib.Vpp 的头布局（已核对源码）：
    o = 5 + 0x14F
    num, container_size, len_offsets, len_filenames, len_extensions = <iiiii> @ o
    names_at   = ((0x800 + len_offsets) & 0xFFFFF800) + 0x800
    ext_at     = ((names_at + len_filenames) & 0xFFFFF800) + 0x800
    data_start = ((ext_at + len_extensions) & 0xFFFFF800) + 0x800
    entry[i]   = <IIiiiii> @ 0x800 + i*28   (a=nameoff, b=extoff, c, body, size, m1, z)
    条目数据   = data_start + body
"""
import os, struct, sys

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

# charlist
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
for w in ("弟兄们", "需要你的保护", "保护他们免遭袭击", "突击", "停靠", "面包车耐久"):
    q = seq(w)
    if q:
        targets[w] = q
print("目标模式:")
for w, q in targets.items():
    print("  %-16s %s" % (w, q.hex(" ")))
print()


def scan(path):
    hits = []
    try:
        f = open(path, "rb")
    except Exception:
        return hits
    with f:
        head = f.read(0x800)
        if len(head) < 0x800 or not head.startswith(b"#VPP"):
            # MAGIC_VPP 可能是别的；退回检查 sr2lib 的 MAGIC
            pass
        o = 5 + 0x14F
        num, csize, lo, lf, le = struct.unpack_from("<iiiii", head, o)
        if num <= 0 or num > 500000:
            return hits
        names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
        ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
        data_start = ((ext_at + le) & 0xFFFFF800) + 0x800
        # 读 entry 表
        chunk = 28 * 20000
        got = 0
        while got < num:
            cnt = min(20000, num - got)
            f.seek(0x800 + got * 28)
            raw = f.read(cnt * 28)
            if len(raw) < cnt * 28:
                break
            for i in range(cnt):
                a, b, c, body, size, m1, z = struct.unpack_from("<IIiiiii", raw, i * 28)
                if size <= 0 or size > 60 * 1024 * 1024:
                    continue
                try:
                    f.seek(data_start + body)
                    d = f.read(size)
                except Exception:
                    continue
                for w, q in targets.items():
                    j = d.find(q)
                    if j >= 0:
                        hits.append((got + i, w, j))
            got += cnt
    return hits


print("=== 扫描所有 VPP ===")
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"):
        continue
    p = os.path.join(G, fn)
    sz = os.path.getsize(p)
    h = scan(p)
    if h:
        print("  ★ %-22s (%6.0f MB) 命中 %d 处" % (fn, sz / 1048576, len(h)))
        for i, w, j in h[:6]:
            print("      条目 #%-6d %s @0x%X" % (i, w, j))
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
