# -*- coding: utf-8 -*-
"""搜索内存中的中文文本，重点定位直升机活动字幕。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:/sr2-cn")
import ce_mini as C

pid = C.find_pid(); h = C.open_process(pid)


def rd(a, n):
    return C.read_mem(h, a, n)


def decode_uni_at(a, maxlen=120):
    b = rd(a, maxlen * 2)
    if not b:
        return None
    out = []
    for i in range(0, len(b) - 1, 2):
        cp = struct.unpack("<H", b[i:i + 2])[0]
        if cp == 0:
            break
        if 32 <= cp < 0xFFFF and not (0xD800 <= cp <= 0xDFFF):
            out.append(chr(cp))
        else:
            out.append(".%04X" % cp if cp >= 0x100 else ".")
    return "".join(out)


targets = ["直升机", "你的弟兄们", "保护", "装甲车", "生命值", "弟兄"]
pats = [(t, t.encode("utf-16-le"), t) for t in targets]
res, _, _, _, _ = C.scan_process(h, pats, C.MAX_ADDR)
for t in targets:
    hits = res.get(t, [])
    print("\n=== %s : %d hits ===" % (t, len(hits)))
    for a in hits[:6]:
        s = decode_uni_at(a - 40, 100)
        print("   0x%08X  ...%s..." % (a, s))
