import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
def parse(p):
    b = open(p,"rb").read().decode("utf-8")
    out = {}; order = []
    cur = None; buf = []
    for line in b.split("\r\n"):
        if line.startswith("[") and line.rstrip().endswith("]"):
            if cur is not None: out[cur] = "\n".join(buf).strip()
            cur = line.strip("[]"); order.append(cur); buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None: out[cur] = "\n".join(buf).strip()
    return out, order
ch, cho = parse(os.path.join(J,"juiced_CH.cxt"))
us, uso = parse(os.path.join(J,"juiced_US.cxt"))
print("US 有但 CH 没有的 key:")
for k in us:
    if k not in ch:
        print("  [%s] = %r" % (k, us[k]))
print()
print("CH 有但 US 没有的 key:")
for k in ch:
    if k not in us:
        print("  [%s] = %r" % (k, ch[k]))
print()
print("US 里无值的 key: %s" % [k for k,v in us.items() if not v])
print("CH 里无值的 key: %s" % [k for k,v in ch.items() if not v])
