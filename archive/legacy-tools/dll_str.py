import re, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = open(os.path.join(G,"DFEngine.dll"),"rb").read()
print("DFEngine.dll %d 字节" % len(b))
# 找 J_ 开头的 key
keys = sorted(set(re.findall(rb'J_[A-Z0-9_]{2,20}', b)))
print("dll 里的 J_ key (%d 个):" % len(keys))
print("  %s" % " ".join(k.decode() for k in keys[:80]))
print()
# 找菜单标签候选（可读英文短语）
cands = set()
for m in re.finditer(rb'[A-Z][A-Za-z0-9 &\'\-\./()]{5,42}', b):
    s = m.group().decode('latin1').strip()
    if s in ("Display & Audio Options","Control Options"): cands.add(s)
print("找到硬编码标签: %s" % sorted(cands))
print()
# 找 Lua 里的 label = "..."
labs = re.findall(rb'label\s*=\s*"([^"]{2,60})"', b)
print("Lua label= 字符串 (%d 个):" % len(labs))
seen=set()
for l in labs:
    s=l.decode('latin1')
    if s not in seen:
        seen.add(s); print("   %s" % s)
    if len(seen)>=60: break
