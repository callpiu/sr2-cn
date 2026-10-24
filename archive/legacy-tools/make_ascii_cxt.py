import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
J = os.path.join(G,"Mods","JUICED - Strings")
OUT = os.path.join(W,"_juice_fix","out6"); os.makedirs(OUT, exist_ok=True)

def parse_raw(p):
    b = open(p,"rb").read().decode("utf-8")
    # 按 [KEY] 切块，保留块内文本
    parts = re.split(r'(?=\[[A-Za-z0-9_,]+\]\r\n)', b)
    out = {}
    for pt in parts:
        m = re.match(r'\[([A-Za-z0-9_,]+)\]\r\n', pt)
        if not m: continue
        out[m.group(1)] = pt[m.end():]
    return out, b
ch, chraw = parse_raw(os.path.join(J,"juiced_CH.cxt"))
us, usraw = parse_raw(os.path.join(J,"juiced_US.cxt"))
print("CH key 数 %d, US key 数 %d" % (len(ch), len(us)))

# 用 US 的英文值替换 CH 的每个值；CH 独有的 key 保留原值
new = []
missing = []
for k in ch:
    if k in us:
        v = us[k]
    else:
        v = ch[k]; missing.append(k)
    if any(ord(c) > 0x100 for c in v):
        v = "(no text)\r\n\r\n"
    new.append("[%s]\r\n%s" % (k, v))
out = "".join(new)
# 保证 CRLF 且与源文件结尾特征一致
out = out.replace("\r\n","\n").replace("\n","\r\n")
if chraw.endswith("\r\n") and not out.endswith("\r\n"): out += "\r\n"
nb = out.encode("utf-8")
p = os.path.join(OUT,"juiced_CH.cxt")
open(p,"wb").write(nb)
print("写出 %s (%d 字节, CR=%d LF=%d)" % (p, len(nb), nb.count(b"\r"), nb.count(b"\n")))
print("CH 独有 key（保留原值）: %s" % missing)
print()
# 校验：所有值是否纯 ASCII
s = nb.decode("utf-8")
bad = [k for k,v in re.findall(r'\[([A-Za-z0-9_,]+)\]\r\n(.*?)(?=\r\n\[|\Z)', s, re.S)
       if any(ord(c) > 0x100 for c in v)]
print("仍含非 ASCII 的 key: %s" % (bad if bad else "无 OK"))
print("key 数: %d" % len(re.findall(r'\[([A-Za-z0-9_,]+)\]', s)))
print()
print("=== 前 14 个条目 ===")
for m in list(re.finditer(r'\[([A-Za-z0-9_,]+)\]\r\n(.*?)(?=\r\n\[|\Z)', s, re.S))[:14]:
    print("  [%-18s] %s" % (m.group(1), " ".join(m.group(2).split())))
