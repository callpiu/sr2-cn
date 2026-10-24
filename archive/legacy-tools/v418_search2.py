"""v418 精确定位：OpenSpy 串 / 圣徒街短记录 / 霰弹枪短记录 / 胞胎 / 登录短记录"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8','replace').split() if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0]==len(nums)-1) else nums
S = {i+SHIFT: chr(c) for i,c in enumerate(cl)}
IDX2CP = {i: c for i,c in enumerate(cl)}

tables = sorted({e['name'] for e in v.entries() if 'CH' in e['name'] and e['ext']=='le_strings'})
for name in tables:
    ent = v.find(name, "le_strings")
    d = v.read(ent)
    b,c,oa,offs = file_offsets(d)
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-24): continue
        u,end = read_units(d, off+8)
        if u is None: continue
        t = "".join(chr(vv) if vv<0x100 else S.get(vv,'\ufffd') for vv,_ in u)
        low = t.lower()
        hit = False; why=""
        if 'openspy' in low: hit=True; why="OpenSpy"
        elif '胞胎' in t: hit=True; why="胞胎"
        elif t.replace(' ','') in ('圣徒街','圣徒','霰弹枪','双管霰弹枪','登录','登入'): hit=True; why="短记录"
        elif '霰弹枪' in t and len(t)<=8: hit=True; why="霰弹枪短"
        elif t=='登录' or t.endswith('登录') and len(t)<=6: hit=True; why="登录短"
        elif '圣徒街' in t and len(t)<=10: hit=True; why="圣徒街短"
        elif '双份' in t or ('食物' in t and len(t)<20): hit=True; why="食物"
        if not hit: continue
        slots = [vv for vv,_ in u]
        print("[%s] @0x%X len=%d %s" % (name, off, len(t), why))
        print("   文本: %r" % t)
        print("   slots: %s" % slots)
        if any(vv>=0x100 for vv in slots):
            print("   坏区间检查: %s" % " ".join(
                "%s@slot%d%s" % (chr(vv) if vv<0x100 else IDX2CP.get(vv-SHIFT,'?'), vv,
                                 " <<<坏区间" if 1073<=vv<=1098 else "")
                for vv in slots if vv>=0x100))
