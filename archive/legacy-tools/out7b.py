import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
OUT = os.path.join(W,"_juice_fix","out7"); os.makedirs(OUT, exist_ok=True)
ch_raw = open(os.path.join(G,"Mods","JUICED - Strings","juiced_CH.cxt"),"rb").read()
us_raw = open(os.path.join(G,"Mods","JUICED - Strings","juiced_US.cxt"),"rb").read()

def parse(b):
    s = b.decode("utf-8")
    # 用 [KEY] 切块（KEY 可含逗号等）
    hits = list(re.finditer(r'\[([A-Za-z0-9_,]+)\]', s))
    out = {}
    for i, m in enumerate(hits):
        end = hits[i+1].start() if i+1 < len(hits) else len(s)
        out[m.group(1)] = s[m.end():end]
    return out
ch = parse(ch_raw); us = parse(us_raw)
print("CH keys %d, US keys %d" % (len(ch), len(us)))
print("CH 最后一个 key: %s" % list(ch)[-1])
print()
# 构造：按 CH 的 key 顺序，值取 US 英文；跳过无值的 key
lines = []
dropped = []
for k in ch:
    v = us.get(k, ch[k])
    if not v.strip():
        dropped.append(k); continue
    v = v.strip("\r\n")
    # 若值里混入了下一个标签，截断
    v = re.sub(r'\[[A-Za-z0-9_,]+\].*$', '', v, flags=re.S).strip()
    if any(ord(c) > 0x7F for c in v):
        v = "(unknown)"
    lines.append("[%s]\r\n%s\r\n\r\n" % (k, v))
out = "".join(lines).rstrip("\r\n") + "\r\n"
nb = out.encode("utf-8")
p = os.path.join(OUT,"juiced_CH.cxt")
open(p,"wb").write(nb)
print("写出 %s (%d 字节, %d keys)" % (p, len(nb), len(lines)))
print("丢弃的无值 key: %s" % dropped)
print("非 ASCII 字符 %d 个" % len([c for c in out if ord(c)>0x7F]))
print()
print("=== 最后 4 个条目 ===")
for m in list(re.finditer(r'\[([A-Za-z0-9_,]+)\]\r\n(.*?)(?=\r\n\r\n|\Z)', out, re.S))[-4:]:
    print("  [%-16s] %r" % (m.group(1), m.group(2)))
print()
print("=== 检查是否还有 MP_SERVER_IP ===")
print("  出现次数: %d" % out.count("MP_SERVER_IP"))
