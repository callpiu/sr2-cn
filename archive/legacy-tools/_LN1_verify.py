# -*- coding: utf-8 -*-
# 决定性验证：字幕 [84F2.87ED] 的槽位流里，第5字/第11字 是否编码错误
# 源(汉化) 你的弟兄们需要你的保护 -> 显示 你的兄弟位需要你的保该
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


cn = Vpp(CN)
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
bi = {c: i for i, c in enumerate(B)}
SRC = "你的弟兄们需要你的保护"
DISP = "你的兄弟位需要你的保该"

for name in ("static_CH", "voice_script_CH", "platform_pc_CH"):
    try:
        d = cn.read(cn.find(name, "le_strings"))
    except Exception:
        continue
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    for i in range(count):
        p = ptrs[i]
        if p + 4 > len(d):
            continue
        id1, id2 = struct.unpack_from("<HH", d, p)
        if (id1, id2) != (0x84F2, 0x87ED):
            continue
        # 解槽位流
        q = p + 4
        sl = []
        while q + 2 <= len(d):
            s, = struct.unpack_from(">H", d, q)
            q += 2
            if s == 0:
                break
            sl.append(s)
        print("=== %s / [84F2.87ED] 槽位数=%d ===" % (name, len(sl)))
        chars = [B[s - 32] if 0 <= s - 32 < len(B) else "{%d}" % s for s in sl]
        print("槽位流:", sl)
        print("解码  :", "".join(chars))
        print()
        print("逐位核对：")
        for n, (s, c) in enumerate(zip(sl, chars), 1):
            exp = SRC[n - 1] if n <= len(SRC) else "?"
            got = DISP[n - 1] if n <= len(DISP) else "?"
            mark = ""
            if c == exp:
                mark = "OK"
            elif c == got:
                mark = "!! 槽位编码错误（解出来就是错字）"
            else:
                mark = "??"
            print("  [%2d] 槽位=%-5d -> %s   期望=%s 实测显示=%s  %s" % (n, s, c, exp, got, mark))
        print()
        print("若槽位编码错误：正确槽位应为 B.index(字)+32")
        for n, ch in enumerate(SRC, 1):
            if n <= len(sl):
                print("  位置%2d '%s' 正确槽位=%d  实际槽位=%d  %s" %
                      (n, ch, bi[ch] + 32 if ch in bi else -1, sl[n - 1],
                       "一致" if ch in bi and sl[n - 1] == bi[ch] + 32 else "★不一致"))
        break
