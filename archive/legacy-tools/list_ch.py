import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
def parse(p):
    b = open(p,"rb").read().decode("utf-8")
    out = {}
    cur = None; buf = []
    for line in b.split("\r\n"):
        if line.startswith("[") and line.rstrip().endswith("]"):
            if cur: out[cur] = "\n".join(buf).strip()
            cur = line.strip("[]"); buf = []
        elif cur is not None:
            buf.append(line)
    if cur: out[cur] = "\n".join(buf).strip()
    return out, b
ch, chraw = parse(os.path.join(J,"juiced_CH.cxt"))
us, usraw = parse(os.path.join(J,"juiced_US.cxt"))
print("CH %d keys, US %d keys" % (len(ch), len(us)))
print()
print("=== CH 里含中文的值 ===")
for k,v in ch.items():
    if any(ord(c)>0x100 for c in v):
        print("  [%-16s] %-24s  -> US: %s" % (k, v, us.get(k,"(US无此key)")))
