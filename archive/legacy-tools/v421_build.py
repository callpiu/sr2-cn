"""v421 完整版：徒/录/弹 渲染坏字 —— patch 槽回退 + common vf3 坏字位修正。

★★★ v418 失败根因（铁证）★★★
游戏渲染用 **common.vpp_pc 的 fnt_chinese.vf3_pc (count=2838)**；
v418 改的是 **patch.vpp_pc 里 count=2795 的废弃副本** ⇒ 静态全绿、实机无效。
  '徒' 坏路径 idx=1026 → common vf3 U/V=(1501,342)
  '建' 正常路径 idx=1026 → common vf3 U/V=(1501,342)   ← 同一格 ⇒ 徒显示成建
  '录'→'底' idx=1013 U/V=(1111,311)；'弹'→'床' idx=1009 U/V=(991,311)
  三者偏移都恰为 32(0x20)，与"控件多减 0x20"吻合。

★ 正确修法（两步，缺一不可）★
① patch.vpp_pc：把 v418 换过的槽【回退到原始槽】
   2288→1090(徒)  2325→1077(录)  2616→1073(弹)
   ⇒ 正常路径 idx = 1058/1045/1041（本来就是正确的徒/录/弹字形）
② common.vpp_pc：把三个"坏字位" vf3[1026/1013/1009] 改成徒/录/弹字形
   ⇒ 坏路径 idx 也正确
   （统计证实 vf3[1013] 只被已废弃的槽1077命中、vf3[1009] 只被1073命中、
     vf3[1026] 无人命中 ⇒ 不影响任何其它字符串）
★ v420 的 GameSpy→OpenSpy 改动保留（与本改动不冲突）。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
PATCH  = os.path.join(GAME, "patch.vpp_pc")
COMMON_BAK = COMMON + ".v420bak"
PATCH_BAK  = PATCH + ".v420bak"
OUT_C = r"F:\sr2-cn\_fix_candidates\common_v421.vpp_pc"
OUT_P = r"F:\sr2-cn\_fix_candidates\patch_v421.vpp_pc"

BACK    = {2288: 1090, 2325: 1077, 2616: 1073}   # v418中间槽 -> 原始槽
VF3_FIX = {1026: 1058, 1013: 1045, 1009: 1041}   # 坏字位 -> 正确字形源 idx

# ============ patch ============
vp = Vpp(PATCH)
cl = [int(s) for s in vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
if not os.path.exists(PATCH_BAK):
    shutil.copy2(PATCH, PATCH_BAK)
    print("✓ 备份 patch ->", PATCH_BAK, "md5", hashlib.md5(open(PATCH_BAK,'rb').read()).hexdigest())
else:
    print("patch 备份已存在 md5", hashlib.md5(open(PATCH_BAK,'rb').read()).hexdigest())

changed = 0; tbl = {}
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
        i = sp; n = len(vp.data); sl = []
        while i + 2 <= n:
            x,y = vp.data[i], vp.data[i+1]
            if x == 0 and y == 0: break
            sl.append((x << 8) | y); i += 2
        if not sl or not any(s in BACK for s in sl): continue
        for j, s in enumerate(sl):
            if s in BACK:
                struct.pack_into('>H', vp.data, sp + j*2, BACK[s])
        changed += 1; tbl[e['name']] = tbl.get(e['name'], 0) + 1
print("✓ patch 槽回退 %d 条记录: %s" % (changed, tbl))
vp.save(OUT_P)
print("  写出", OUT_P, "md5", hashlib.md5(open(OUT_P,'rb').read()).hexdigest())

# ============ common ============
vc = Vpp(COMMON)
e = vc.find("fnt_chinese", "vf3_pc"); co = vc.data_start + e['body']
N = struct.unpack_from('<I', vc.data, co + 0x08)[0]
assert N == 2838, N
def uv(d, i): return (struct.unpack_from('<i', d, co+0xAF6C+i*4)[0],
                      struct.unpack_from('<i', d, co+0xDB18+i*4)[0])
def rc(d, i): return struct.unpack_from('<IIII', d, co+0xD0+i*16)
if not os.path.exists(COMMON_BAK):
    shutil.copy2(COMMON, COMMON_BAK)
    print("✓ 备份 common ->", COMMON_BAK, "md5", hashlib.md5(open(COMMON_BAK,'rb').read()).hexdigest())
else:
    print("common 备份已存在 md5", hashlib.md5(open(COMMON_BAK,'rb').read()).hexdigest())
print("\ncommon vf3 改前 -> 改后:")
for d, s in VF3_FIX.items():
    print("  vf3[%d] %s  ->  src%d %s" % (d, uv(vc.data,d), s, uv(vc.data,s)))
for d, s in VF3_FIX.items():
    u, w = uv(vc.data, s)
    struct.pack_into('<i', vc.data, co+0xAF6C+d*4, u)
    struct.pack_into('<i', vc.data, co+0xDB18+d*4, w)
    struct.pack_into('<IIII', vc.data, co+0xD0+d*16, *rc(vc.data, s))
vc.save(OUT_C)
print("✓ 写出", OUT_C, "md5", hashlib.md5(open(OUT_C,'rb').read()).hexdigest())

# ============ 校验 ============
print("\n=== 校验：三条路径全部正确 ===")
v2 = Vpp(OUT_C); e2 = v2.find("fnt_chinese","vf3_pc"); c2 = v2.data_start + e2['body']
def nUv(i): return (struct.unpack_from('<i', v2.data, c2+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', v2.data, c2+0xDB18+i*4)[0])
want = {'徒': nUv(1058), '录': nUv(1045), '弹': nUv(1041)}
for ch, slot in (('徒',1090), ('录',1077), ('弹',1073)):
    a, b = nUv(slot-0x20), nUv(slot-0x40)
    good = (a == want[ch] and b == want[ch])
    print("  %r 槽%d: 正常idx%d=%s 坏idx%d=%s 目标=%s  %s" %
          (ch, slot, slot-0x20, a, slot-0x40, b, want[ch], "OK" if good else "★"))
    assert good, ch
vp2 = Vpp(OUT_P)
left = 0; right = 0
for e in vp2.entries():
    if e['ext'] != 'le_strings' or '_CH' not in e['name']: continue
    b = vp2.read(e)
    try: bc,c,oa,offs = file_offsets(b)
    except: continue
    body = vp2.data_start + e['body']; seen=set()
    for off in offs:
        sp = body + off + 8
        if sp in seen: continue
        seen.add(sp)
        if not (body < sp <= len(vp2.data) - 24): continue
        i=sp; n=len(vp2.data)
        while i+2<=n:
            x,y=vp2.data[i],vp2.data[i+1]
            if x==0 and y==0: break
            s=(x<<8)|y
            if s in BACK: left += 1
            if s in BACK.values(): right += 1
            i+=2
print("  残留中间槽: %d (应0)   原始槽出现: %d" % (left, right))
assert left == 0
print("\n✓ v421 完整构建完成（候选，未部署）")