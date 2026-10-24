import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units, decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
CL = CharList(CPS)
RAW = {c: i for i, c in enumerate(CPS)}
for tname in ("Menus_text","HUD_text","Controls_text"):
    e = v.find(tname)
    if not e: print("  %s 未找到" % tname); continue
    d = bytes(v.read(e))
    b,c,oa,offs = file_offsets(d)
    recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        recs.append((off,u))
    # 解码为【码点】形式（原始值就是码点? 试两种）
    txt_cp = []
    for off,u in recs:
        t = "".join(chr(x) for x,_ in u if 0x20 <= x < 0x10000 and x not in (0,))
        txt_cp.append(t)
    joined = "\n".join(txt_cp)
    hit_t = "SUI_OPTIONS_TITLE" in joined
    hit_l = "SUI_LOADING" in joined
    print("  %-16s %7d 字节, %5d 条记录, 含 SUI_OPTIONS_TITLE=%s, 含 SUI_LOADING=%s" % (
        tname, len(d), len(recs), hit_t, hit_l))
    # 找含音效音量的记录
    for off,u in recs:
        t = "".join(chr(x) for x,_ in u if 0x20 <= x < 0x10000)
        if "音效音量" in t or "SUI_OPTIONS_TITLE" in t:
            print("      @%d %r (原始值前 12: %s)" % (off, t[:40], [x for x,_ in u][:12]))
            break
