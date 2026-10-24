# -*- coding: utf-8 -*-
"""验证 build_patterns 构造的字节是否正确（不依赖游戏进程）"""
import sys, struct
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

C.CL = C.load_charlist()
print("字表 %d 项" % len(C.CL))

# 交叉验证：直接从游戏中当前的 REC1 读出真实字节
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp = S.Vpp(game + "patch.vpp_pc")
ent = vp.find("static_CH", "le_strings"); d = bytes(vp.read(ent))
magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
offs = [struct.unpack_from("<I", d, 12 + buckets*8 + k*4)[0] for k in range(count)]
real = None
for off in dict.fromkeys(offs):
    i1, i2 = struct.unpack_from("<HH", d, off)
    if ((i1<<16)|i2) == 0x84F287ED:
        p = off+4; vals=[]
        while True:
            s = struct.unpack_from(">H", d, p)[0]
            if s == 0: break
            vals.append(s); p += 2
        real = b"".join(struct.pack(">H", s) for s in vals)
print("磁盘真实 REC1 前 24 字节:", real[:24].hex(" ").upper())

for name, pat, note in C.build_patterns():
    found = "✓ 能在真实REC1中找到" if real and pat in real else ""
    print("\n%-22s %-14s %s" % (name, (pat[:24].hex(" ").upper() + ("…" if len(pat) > 24 else "")), found))
    print("    %d 字节  %s" % (len(pat), note))

p1 = C.slots_be("你的") + C.be("[f")
print("\n★ 关键自检：slots_be('你的')+be('[f') =", p1.hex(" ").upper())
assert real and real.startswith(p1), "模式与磁盘真实字节不符！"
print("  与磁盘真实 REC1 开头完全一致 ✓   -> 脚本 Sure hit 能力已验证")
