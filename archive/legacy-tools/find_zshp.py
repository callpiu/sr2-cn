import os, re, struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
exe = open(os.path.join(G,"SR2_pc.exe"),"rb").read()
for tag, s in (("zSHP","zSHP"), ("ChopShop","ChopShop"), ("map_mp_bor_chopshop","map_mp_bor_chopshop")):
    p16 = s.encode("utf-16-le")
    p8 = s.encode()
    print("=== %s ===" % tag)
    print("  UTF-16 %s: %s" % (p16.hex(" "), ("0x%X" % exe.find(p16)) if exe.find(p16)>=0 else "未找到"))
    print("  ASCII  %s: %s" % (p8.hex(" "), ("0x%X" % exe.find(p8)) if exe.find(p8)>=0 else "未找到"))
print()
# 在 exe 里搜所有 "<img " 的 UTF-16
p = "<img ".encode("utf-16-le")
hits = [m.start() for m in re.finditer(re.escape(p), exe)]
print("exe 里 UTF-16 \"<img \" 出现 %d 次" % len(hits))
for h in hits[:6]:
    seg = exe[h:h+120].decode("utf-16-le","ignore")
    print("  0x%X: %r" % (h, seg.split("\x00")[0][:60]))
