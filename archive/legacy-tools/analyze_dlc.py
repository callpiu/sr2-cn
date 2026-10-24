"""实证：DLC/Mods 的中文 le_strings 表，用繁体(2841) vs 简体(2795) 字表解码。

若某表在【繁体】下解码正常、在【简体】下大量越界 → 证实：这些表按繁体表编码，
但汉化 patch 换了简体字表 → 槽位越界 → 崩溃。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import parse_charlist
from sr2patch import file_offsets, read_units, SHIFT

VANILLA = r"F:\sr2-cn\_day_2026-10-07\07_备份快照\patch.vpp_pc.原版_能跑_2320.bak"
LOCAL  = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"

def get_cl(path, name="charlist_CH", ext="txt"):
    # charlist 在 vpp 内；这里只从两个 patch 取
    from sr2lib import Vpp
    v = Vpp(path)
    e = v.find(name, ext)
    if not e: return None
    nums = [int(x) for x in v.read(e).decode('utf-8','replace').split()
            if x.strip().lstrip('-').isdigit()]
    return nums[1:] if nums and nums[0] == len(nums)-1 else nums

cl_trad = get_cl(VANILLA)   # 2841
cl_simp = get_cl(LOCAL)     # 2795
print("繁体=%d  简体=%d" % (len(cl_trad), len(cl_simp)))
rev_trad = {i+SHIFT: chr(c) for i,c in enumerate(cl_trad)}
rev_simp = {i+SHIFT: chr(c) for i,c in enumerate(cl_simp)}

def stats(path, revmap, count, label):
    d = open(path,'rb').read()
    if struct.unpack_from('<I', d, 0)[0] != 0xA84C7F73:
        # .cxt 不是 le_strings 格式
        print("  [跳过] %s 不是 le_strings 格式 (magic=%r)" % (label, d[:4]))
        return
    buckets, cnt, off_at, offs = file_offsets(d)
    ok=bad=0; samples_ok=[]; samples_bad=[]
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        units,_ = read_units(d, off+8)
        if units is None: continue
        txt=[]; recbad=False
        for vv,_ in units:
            if vv < 0x100: txt.append(chr(vv))
            else:
                idx=vv-SHIFT
                if 0<=idx<count: txt.append(revmap.get(vv,'\ufffd'))
                else: recbad=True; txt.append('\ufffd')
        if recbad:
            bad+=1
            if len(samples_bad)<2: samples_bad.append(''.join(txt)[:50])
        else:
            ok+=1
            s=''.join(txt)
            if any(ord(c)>0x100 for c in s) and len(samples_ok)<3:
                samples_ok.append(s[:50])
    print("  %-22s 记录 OK=%d BAD=%d" % (label, ok, bad))
    for s in samples_ok: print("      简/繁可解样本: %s" % s)
    for s in samples_bad: print("      越界样本: %s" % s)

BASE = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
files = [
    (os.path.join(BASE,"DLC/Text/dlc_ch.le_strings"), "DLC/Text/dlc_ch"),
    (os.path.join(BASE,"Mods/JUICED - Strings/patch_ch.le_strings"), "Mods/patch_ch"),
    (os.path.join(BASE,"Mods/JUICED - Strings/juiced_CH.le_strings"), "Mods/juiced_CH"),
]
for p,label in files:
    if not os.path.exists(p):
        print("缺失 %s" % p); continue
    print("== %s ==" % label)
    print("  -- 用繁体字表(2841) --"); stats(p, rev_trad, len(cl_trad), label+"[繁]")
    print("  -- 用简体字表(2795) --"); stats(p, rev_simp, len(cl_simp), label+"[简]")
