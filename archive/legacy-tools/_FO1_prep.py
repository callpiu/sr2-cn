import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")

def parse(b, T):
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    nc = (len(b) - start) // 2
    codes = list(struct.unpack_from(">%dH" % nc, b, start))
    out = []; cur = []; st = 0
    for i, c in enumerate(codes):
        if c == 0:
            out.append((st, i, "".join(cur))); cur = []; st = i + 1
        elif c < 32:
            cur.append("")
        elif c - 32 < len(T):
            cur.append(chr(T[c - 32]))
        else:
            cur.append("~")
    return out, codes, start

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
chb = vp.read(vp.find("static_CH", "le_strings"))
usb = vp.read(vp.find("static_US", "le_strings"))
ch, chc, chs = parse(chb, M)
us, usc, uss = parse(usb, M)
print("CH pieces=%d  US pieces=%d  CHsize=%d USsize=%d" % (len(ch), len(us), len(chb), len(usb)))
print()

KEY1 = "".join(chr(c) for c in [0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4])
KEY2 = "".join(chr(c) for c in [0x8981, 0x51FA, 0x53BB, 0x8C08, 0x51E0, 0x7B14, 0x751F, 0x610F])

targets = []
for i, (st, en, s) in enumerate(ch):
    if KEY1 in s or KEY2 in s:
        targets.append(i)

for i in targets:
    st, en, s = ch[i]
    print("=" * 70)
    print("CH piece #%d   codes[%d..%d)  span=%d" % (i, st, en, en - st))
    print("  decoded:", s)
    print("  prefix codes:", chc[st:st+2], " (decoded:", s[:2], ")")
    print("  text codes:", chc[st+2:en], " count=", en - st - 2)
    print("  text decoded:", s[2:])
    print("  id bytes:", chb[chs + st*2: chs + st*2 + 4].hex())
    if i < len(us):
        ust, uen, us_ = us[i]
        print("  US same-index #%d:" % i)
        print("     decoded:", us_[2:] if len(us_) > 2 else us_)
        print("     codes:", usc[ust:uen], " count=", uen - ust)
    # by id
    idb = chb[chs + st*2: chs + st*2 + 4]
    for j, (ust, uen, us_) in enumerate(us):
        if usb[uss + ust*2: uss + ust*2 + 4] == idb:
            print("  US by id (piece #%d): %s" % (j, us_[2:] if len(us_) > 2 else us_))
            print("     codes:", usc[ust:uen])
            break
    print()
