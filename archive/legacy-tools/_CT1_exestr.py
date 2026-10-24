import re
EXE = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
data = open(EXE, "rb").read()
print("exe size", len(data))
for pat in (b"font_info", b"alias", b"filename_overlay", b"filename", b"vint_proj", b"charlist_%s", b"count=%u", b"%hu", b"sr2.vint_proj"):
    hits = [m.start() for m in re.finditer(re.escape(pat), data)]
    print("%-18s 命中 %d 处" % (pat.decode(), len(hits)))
    for h in hits[:6]:
        # 前后文
        ctx = data[max(0, h-24):h+len(pat)+24]
        print("     0x%X  %r" % (h, ctx))
