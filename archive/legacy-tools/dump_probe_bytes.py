# -*- coding: utf-8 -*-
"""导出当前 REC1 探针的原始 slot 字节，供 CE 搜索用"""
import sys, struct, re
sys.path.insert(0, "F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp = S.Vpp(game + "patch.vpp_pc")
buf = vp.read(vp.find("charlist_CH", "txt")); end = buf.find(b"//ENDOFFILE")
cl = [int(x) for x in re.findall(rb"\d+", buf[:end if end > 0 else len(buf)])]
ent = vp.find("static_CH", "le_strings"); d = bytes(vp.read(ent))
magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
offs = [struct.unpack_from("<I", d, 12 + buckets * 8 + k * 4)[0] for k in range(count)]
for off in dict.fromkeys(offs):
    id1, id2 = struct.unpack_from("<HH", d, off)
    h = (id1 << 16) | id2
    if h != 0x84F287ED: continue
    p = off + 4; vals = []
    while True:
        s = struct.unpack_from(">H", d, p)[0]
        if s == 0: break
        vals.append(s); p += 2
    raw = b"".join(struct.pack(">H", s) for s in vals) + b"\x00\x00"
    print("REC1 hash=0x84F287ED  槽位=%d" % len(vals))
    print("  解码:", repr("".join(chr(s) if 0x20<=s<=0x7E else chr(cl[s-0x20]) for s in vals)))
    print("  槽位:", " ".join("%d(%#x)" % (s, s) for s in vals))
    print()
    print("  ★ CE Byte Array 搜索（含终止符，共 %d 字节）:" % len(raw))
    print("   ", " ".join("%02X" % b for b in raw))
    print()
    print("  ★ CE 可粘贴的字节串:")
    print("   ", raw.hex().upper())
    print()
    # 纯 ASCII 部分（去掉前 2 个中文）
    ascii_part = b"".join(struct.pack(">H", s) for s in vals if 0x20 <= s <= 0x7E)
    print("  ASCII 部分 UTF-16BE 字节:", " ".join("%02X" % b for b in ascii_part))
    le = b"".join(struct.pack("<H", s) for s in vals if 0x20 <= s <= 0x7E)
    print("  若游戏已转成 UTF-16LE，则搜 Unicode 串:", le.decode("utf-16-le"))
