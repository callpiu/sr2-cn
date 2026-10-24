import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
B = r"F:/sr2-cn/_day_2026-10-07/07_备份快照/Mods残留_20261009"
cands = {
 "3615":  r"F:/sr2-cn/fontwork/charlist_final.bin",
 "3610":  r"F:/sr2-cn/fontwork/charlist_new.bin",
 "3611":  r"F:/sr2-cn/_archive/output/charlist_CH",
 "2839":  r"F:/sr2-cn/_archive/output_final/charlist_CH",
}
tables={}
for k,p in cands.items():
    if not os.path.exists(p): print("缺",k,p); continue
    raw=open(p,"rb").read()
    cps=[int(l) for l in raw.decode("utf-8",errors="ignore").split("\n") if l.strip().isdigit()]
    tables[k]=cps
    print("字表 %s: %d 项, 前20=%r" % (k, len(cps), "".join(chr(c) for c in cps[:20])))
print()
for fname in ("static_CH.le_strings.v44bak","static_CH.le_strings.v45bak"):
    d=open(os.path.join(B,fname),"rb").read()
    print("=== %s ===" % fname)
    for k,cps in tables.items():
        S={i+0x20:chr(c) for i,c in enumerate(cps)}
        def dec(vals): return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
        try: b,c,oa,offs=file_offsets(d)
        except Exception as ex: print("  字表%s 解析失败" % k); continue
        found=[]
        for off in dict.fromkeys(offs):
            if not (0<off<=len(d)-10): continue
            u,_=read_units(d,off+8)
            if u is None: continue
            t=dec([x for x,_ in u])
            if "辩护延师" in t or "丈王" in t or "辩护律师" in t or "三王" in t:
                found.append((off,t[:60]))
        if found:
            print("  字表%s 命中 %d 条:" % (k,len(found)))
            for off,t in found[:6]: print("     @%-8d %r" % (off,t))
    print()
