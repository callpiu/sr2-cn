import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
p = os.path.join(M,"city_load.lua")
b = open(p,"rb").read()
txt = b.decode("gbk")
# 打印所有非 ASCII 段
seqs = []
j = 0
while j < len(txt):
    if ord(txt[j]) > 0x7F:
        st = j
        while j < len(txt) and ord(txt[j]) > 0x7F: j += 1
        seqs.append(txt[st:j])
    else:
        j += 1
print("非 ASCII 段 %d 个:" % len(seqs))
for s in seqs[:60]:
    print("  %r" % s)
