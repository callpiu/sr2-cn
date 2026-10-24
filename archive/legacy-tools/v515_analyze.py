"""v515：★★ 坏字根治（复现并推广 v422 的双槽冗余方案）★★

★★★ 关键突破：用户确认「v422 时主菜单是正常的」★★★
v422 当时的组合 = patch(字表6处改码点 + 字符串换槽) + common(vf3 6处重指)
                  + textures(官方原版，未改)

★ v422 为什么有效（本次已完全解码）★
它用的是【双槽冗余】：让同一汉字占据相差 32 (=0x20) 的两个索引。
    徒: charlist[653]=徒, charlist[685]=徒 ;  vf3[653]=徒字形, vf3[685]=徒字形
    字符串用 slot717 -> 引擎取 idx717-0x20=685 (徒)
                      -> 若引擎再多减 0x20 取 idx653 (也是徒) ⇒ 结果仍是徒
★ 而我 v418/v421 只改了"正常索引"，没管"多减 0x20 的那个索引" ⇒ 失效。

★★★ 现在的任务：把这套方案推广到【所有坏字】★★★
用户截图（主菜单）：约级/推选超/躬做选超/卖们/囷争选超/通领/槍刀
已知坏字对：徒→建 录→底 弹→床 阶→约 我→卖 缉→领 撬棍→槍刀
做法（对每个【正确字 X】）：
  1) 找出 X 在字表里的所有"被误取"风险位 = idx(X) 及其 idx-32 链上的空闲位
  2) 把该位在 charlist 与 vf3 中都指向 X
限定条件：只动【当前字表里本就是废字/未被任何字符串引用】的位置，绝不牺牲在用汉字。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
COMMON_BAK = COMMON + ".official_bak"
PATCH_BAK  = PATCH + ".v513.bak"
OUT_C = r"F:\sr2-cn\_fix_candidates\common_v515.vpp_pc"
OUT_P = r"F:\sr2-cn\_fix_candidates\patch_v515.vpp_pc"

BASE_PATCH = os.path.join(GAME, "patch.vpp_pc")   # = v513(干净基线 + GameSpy修正)

# ---------- 载入 ----------
vp = Vpp(BASE_PATCH)
cl_lines = vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n')
cl = [int(s) for s in cl_lines if s.strip().isdigit()]
CLLEN = len(cl)
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)

vc = Vpp(COMMON)
ec = vc.find("fnt_chinese","vf3_pc"); co = vc.data_start + ec['body']
NC = struct.unpack_from('<I', vc.data, co + 0x08)[0]
def cuv(i): return (struct.unpack_from('<i', vc.data, co+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', vc.data, co+0xDB18+i*4)[0])
def crec(i): return struct.unpack_from('<IIII', vc.data, co+0xD0+i*16)

print("patch 字表 %d 条 ; common vf3 %d 条" % (CLLEN, NC))

# ---------- 统计 CH 字符串用到的槽 ----------
used = set()
for e in vp.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = vp.read(e)
    try: bc,c,oa,offs = file_offsets(b)
    except: continue
    body = vp.data_start + e['body']; seen = set()
    for off in offs:
        sp = body + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(vp.data) - 24): continue
        i = sp; n = len(vp.data)
        while i + 2 <= n:
            x,y = vp.data[i], vp.data[i+1]
            if x == 0 and y == 0: break
            used.add((x << 8) | y); i += 2
print("CH 已用槽 %d 个" % len(used))

# ---------- 坏字清单（正确字 -> 实际显示的错字）----------
BAD = [('徒','建'), ('录','底'), ('弹','床'),
       ('阶','约'), ('我','卖'), ('缉','领'), ('棍','刀')]
print("\n=== 坏字清单与风险索引 ===")
plan = {}
for good, bad in BAD:
    gs = c2s.get(good); bs = c2s.get(bad)
    if gs is None:
        print("  %r 不在字表，跳过" % good); continue
    gi = gs - 0x20                     # 正常索引
    risk = gi - 0x20                   # 多减 0x20 的索引
    # 风险位对应的"原住民"是谁、是否被字符串占用
    orig = chr(cl[risk]) if 0 <= risk < CLLEN else '?'
    busy = (risk + 0x20) in used
    ok = (not busy) and 0 <= risk < NC and risk < CLLEN
    plan[good] = dict(good=good, bad=bad, gslot=gs, gidx=gi, risk=risk,
                      orig=orig, busy=busy, ok=ok)
    print("  %r→%r  正常idx%d(vf3%s)  风险idx%d=原%r 该槽被引用=%s  %s" % (
        good, bad, gi, cuv(gi), risk, orig, busy, "可用" if ok else "★占用"))

print("\n可用风险位: %s" % [g for g,d in plan.items() if d['ok']])
print("被占用需另选: %s" % [g for g,d in plan.items() if not d['ok']])