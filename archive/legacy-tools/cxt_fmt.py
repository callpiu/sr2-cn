import re, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
J = os.path.join(G,"Mods","JUICED - Strings")
for f in ("juiced_CH.cxt","juiced_CH.cxt.before_keyfix","juiced_US.cxt"):
    p=os.path.join(J,f)
    if not os.path.exists(p): continue
    b=open(p,"rb").read()
    print("=== %s (%d 字节, CR=%d LF=%d) ===" % (f,len(b),b.count(b"\r"),b.count(b"\n")))
    # 看条目分隔结构
    print("  前 60 字节: %r" % b[:60])
    print("  J_OPTIONS 前后: %r" % b[:80])
    # 空行数量
    print("  连续 \\r\\n 的最大串: %r" % max(re.findall(rb'(?:\r\n){2,}', b), key=len))
    print("  末 40 字节: %r" % b[-40:])
    print()
