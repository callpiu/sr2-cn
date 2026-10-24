import sys, os, struct, collections
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, parse_charlist
from sr2patch import CharList, file_offsets, read_units, decode
W = r"F:\sr2-cn"
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
CPS0 = parse_charlist(v0.read(v0.find("charlist_CH","txt")))
CL0 = CharList(CPS0)
# 第三方
raw = open(os.path.join(W,"_juice_fix","charlist_CH.txt"),"rb").read().decode("utf-8")
CP3 = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
print("原厂 charlist %d 项；第三方 %d 项" % (len(CPS0), len(CP3)))
print()
# 第三方文本：用第三方 charlist 解码，收集用到的字符
v3 = Vpp(r"F:\sr2-cn\_juice_fix\patch.vpp_pc")
files = ["static_CH","voice_script_CH","platform_pc_CH"]
used = collections.Counter()
recs = {}
for nm in files:
    e = v3.find(nm,"le_strings")
    if not e: print("  %s 未找到" % nm); continue
    d = bytes(v3.read(e))
    b,c,oa,offs = file_offsets(d)
    L = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        L.append((off, u))
    recs[nm] = L
    print("  %-18s %6d 字节  %5d 条记录" % (nm, len(d), len(L)))
print()
# 解码（第三方 charlist：slot = 索引+0x20）
def dec3(u):
    out=[]
    for x,_p in u:
        i = x - 0x20
        out.append(chr(CP3[i]) if 0 <= i < len(CP3) else "\uFFFD")
    return "".join(out)
tot=0; miss=set()
for nm,L in recs.items():
    for off,u in L:
        t = dec3(u)
        tot += 1
        for ch in t:
            if 0x100 < ord(ch) < 0x9FFF or ch in "！（）《》，／：；？":
                used[ch] += 1
                if ord(ch) not in CL0.rev: miss.add(ch)
print("第三方文本共 %d 条，用到不同字符 %d 个（含标点）" % (tot, len(used)))
print("其中【不在原厂繁中字表】的: %d 个" % len(miss))
print("  %s" % "".join(sorted(miss))[:120])
print()
# 这些缺字里，有多少能用繁体对应字替代
from opencc import OpenCC
s2t = OpenCC("s2t")
ok=[]; no=[]
for ch in sorted(miss):
    t = s2t.convert(ch)
    if len(t)==1 and ord(t) in CL0.rev: ok.append((ch,t))
    else: no.append(ch)
print("能用繁体对应字替代: %d 个" % len(ok))
print("  例: %s" % " ".join("%s->%s"%(a,b) for a,b in ok[:25]))
print("无法替代: %d 个 -> %s" % (len(no), "".join(no)[:100]))
