import os, re, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
# 收集所有 lua 里的 SUI_ key
keys = set()
for f in os.listdir(M):
    if f.endswith(".lua"):
        try: s = open(os.path.join(M,f), encoding="utf-8", errors="replace").read()
        except Exception: continue
        keys |= set(re.findall(r'"(SUI_[A-Z0-9_]+)"', s))
print("所有 lua 里引用的 SUI_ key: %d 个" % len(keys))
print()
# 检查这些 key 是否在 patch.vpp_pc 的 le_strings 里（以字符串形式或 hash 形式）
v = Vpp(G + r"\patch.vpp_pc")
blobs = {}
for e in v.entries():
    if e["ext"] == "le_strings":
        blobs[e["name"]] = bytes(v.read(e))
print("检查 key 是否以明文出现在任何 le_strings 里...")
found = {}
for k in sorted(keys):
    kb = k.encode()
    hit = [nm for nm, b in blobs.items() if kb in b]
    if hit: found[k] = hit
print("  明文命中的 key: %d 个" % len(found))
for k, v2 in list(found.items())[:10]: print("    %s -> %s" % (k, v2))
print()
# 这些 le_strings 有没有可能用 hash？先看是否有 ASCII 文本
print("=== le_strings 里是否含明文 ASCII ===")
for nm, b in list(blobs.items())[:6]:
    runs = re.findall(rb'[A-Z][A-Z0-9_]{6,40}', b)
    print("  %-20s 明文大写标识符 %d 个 %s" % (nm, len(runs), [r.decode() for r in runs[:3]]))
