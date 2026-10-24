import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")
IDS = (0xF284ED87, 0xAF10621E)

def scan(tag, b, T, show_all=False):
    try:
        n = struct.unpack_from("<I", b, 8)[0]
    except Exception:
        return
    if not (0 < n < 500000):
        return
    start = 16 + n * 8
    if start >= len(b):
        return
    nc = (len(b) - start) // 2
    codes = struct.unpack_from(">%dH" % nc, b, start)
    st = 0
    for i, c in enumerate(codes):
        if c == 0:
            if i - st >= 3:
                idv = (codes[st] << 16) | codes[st+1]
                if idv in IDS:
                    s = "".join(chr(T[x-32]) if x >= 32 and x-32 < len(T) else "" for x in codes[st+2:i])
                    print("  [%s] id=0x%08X  %s" % (tag, idv, s[:130]))
            st = i + 1

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
print("=== VPP 内所有字符串文件按 ID 搜索 ===")
for e in vp.entries():
    if "string" in (e.get("ext") or ""):
        b = vp.read(e)
        scan(e["name"] + "(M)", b, M)
        scan(e["name"] + "(O)", b, O)

print()
print("=== 松散文件 ===")
loose = [r"Mods\static_US.le_strings", r"Mods\platform_PC_US.le_strings",
         r"Mods\JUICED - Strings\patch_ch.le_strings", r"Mods\JUICED - Strings\juiced_CH.le_strings"]
for rel in loose:
    p = os.path.join(G, rel)
    if os.path.exists(p):
        b = open(p, "rb").read()
        scan(os.path.basename(rel) + "(M)", b, M)
        scan(os.path.basename(rel) + "(O)", b, O)
print("done")
