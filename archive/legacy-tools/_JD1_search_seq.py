# -*- coding: utf-8 -*-
# 在全游戏文件中搜索：固定索引序列 / 期望文本 / 显示文本 的字节形态
import os, struct, glob

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

TEXT_EXPECT = "你的兄弟們需要你的保護"
TEXT_DISP_CN = "任璨偶巧位雄衡任璨伪该"
TEXT_DISP_OFF = "使發光彈借雇複使發俱謗"

J = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]
JSLOT = [x + 0x20 for x in J]

pats = []
pats.append(("J  as u16 BE", b"".join(struct.pack(">H", x) for x in J)))
pats.append(("J  as u16 LE", b"".join(struct.pack("<H", x) for x in J)))
pats.append(("J+0x20 BE", b"".join(struct.pack(">H", x) for x in JSLOT)))
pats.append(("J+0x20 LE", b"".join(struct.pack("<H", x) for x in JSLOT)))
pats.append(("J  as u32 LE", b"".join(struct.pack("<I", x) for x in J)))
pats.append(("J  as u32 BE", b"".join(struct.pack(">I", x) for x in J)))
for tag, t in [("期望文本", TEXT_EXPECT), ("汉化显示文本", TEXT_DISP_CN), ("官方显示文本", TEXT_DISP_OFF)]:
    pats.append((tag + " UTF-16LE", t.encode("utf-16-le")))
    pats.append((tag + " UTF-16BE", t.encode("utf-16-be")))
    pats.append((tag + " UTF-8", t.encode("utf-8")))
# 只取前 6 个槽位（较短的指纹），用于模糊命中
pats.append(("前6槽 BE", b"".join(struct.pack(">H", x) for x in JSLOT[:6])))
pats.append(("前4槽 BE", b"".join(struct.pack(">H", x) for x in JSLOT[:4])))

targets = []
targets += sorted(glob.glob(os.path.join(G, "*.vpp_pc")))
targets += sorted(glob.glob(os.path.join(G, "*.exe")))
targets += sorted(glob.glob(os.path.join(G, "*.dll")))
print("扫描目标 %d 个文件\n" % len(targets))

for path in targets:
    try:
        data = open(path, "rb").read()
    except Exception as ex:
        print("[跳过]", path, ex)
        continue
    hits = []
    for tag, p in pats:
        if not p:
            continue
        st = 0
        cnt = 0
        first = []
        while True:
            q = data.find(p, st)
            if q < 0:
                break
            cnt += 1
            if len(first) < 6:
                first.append(q)
            st = q + 1
            if cnt > 5000:
                break
        if cnt:
            hits.append("    %-22s x%-5d 首地址=%s" % (tag, cnt, [hex(x) for x in first]))
    if hits:
        print("### %s  (%d bytes)" % (os.path.basename(path), len(data)))
        print("\n".join(hits))
        print()
