import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
p = os.path.join(M,"pause_menu.lua")
b = open(p,"rb").read()
# 找 音效选项 的 GBK 字节 D2F4D0A7D1A1CFEE
for key, desc in ((bytes.fromhex("d2f4d0a7d1a1cfee"), "音效选项(GBK)"),
                  (bytes.fromhex("e99fb3e69588e98089e9a1b9"), "音效选项(UTF-8)"),
                  (bytes.fromhex("c9c6d3c3"), "善用(GBK)")):
    i = b.find(key)
    print("  %-22s %s" % (desc, ("偏移 %d" % i) if i >= 0 else "未找到"))
print()
# 找 "音效选项" 这个字符串出现的地方，打印原始字节
i = b.find(bytes.fromhex("d2f4d0a7d1a1cfee"))
if i >= 0:
    print("  GBK 命中处原始字节: %s" % b[i-8:i+16].hex(" "))
    print("  上下文: %r" % b[i-8:i+16])
print()
# 列出文件里所有非 ASCII 字节对
seqs = []
j = 0
while j < len(b):
    if b[j] > 0x7F:
        st = j
        while j < len(b) and b[j] > 0x7F: j += 1
        seqs.append((st, b[st:j]))
    else:
        j += 1
print("  非 ASCII 连续段 %d 个:" % len(seqs))
for st, s in seqs[:10]:
    try: dec = s.decode("gbk")
    except Exception: dec = "?"
    print("    @%-8d %-30s -> %r" % (st, s.hex(" ")[:30], dec))
