"""v421 终版：修徒/录/弹 渲染坏字 —— ★只改 common.vpp_pc 的 fnt_chinese.vf3_pc★

★★ v418 失败铁证 ★★
游戏渲染用 common.vpp_pc 的 vf3(count=2838)，v418 改的是 patch.vpp_pc 里的
count=2795 废弃副本 ⇒ 像素级校验全过但实机毫无变化。
证据：'徒'坏路径idx=1026 → common vf3 U/V=(1501,342) == '建'正确路径 U/V ⇒ 显示成"建"。

★ 本版思路（更简洁、更安全）★
v418 已把字符串槽 1090/1077/1073 → 2288/2325/2616（这些新槽在 common vf3 里
指向随机字形）。而 vf3[1026/1013/1009] 这三个"坏字位置"经全盘统计：
    vf3[1026] 被 0 个槽经坏路径命中
    vf3[1013] 只被【槽 1077】命中 —— 槽 1077 已废弃(无任何字符串再用)
    vf3[1009] 只被【槽 1073】命中 —— 同上
⇒ 直接把 vf3[1026/1013/1009] 的 U/V/<IIII> 改成 徒/录/弹 的真实字形即可，
   ★ 不需要动任何字符串、不需要找空闲槽对 ★，且对现有 2288/2325/2616 零影响
   （它们走 2256/2224、2293/2261、2584/2552，与 1026/1013/1009 无关）。

保留：v420 的 GameSpy→OpenSpy 改动（在 patch 里）。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
COMMON = os.path.join(GAME, "common.vpp_pc")
BAK = COMMON + ".v420bak"
OUT_C = r"F:\sr2-cn\_fix_candidates\common_v421.vpp_pc"

# 坏字位置 -> 目标字源 idx（common vf3 内的正确路径索引）
FIX = {1026: 1058,   # 建位 -> 徒
       1013: 1045,   # 底位 -> 录
       1009: 1041}   # 床位 -> 弹

vc = Vpp(COMMON)
e = vc.find("fnt_chinese", "vf3_pc")
co = vc.data_start + e['body']
N = struct.unpack_from('<I', vc.data, co + 0x08)[0]
assert N == 2838, N
print("common vf3 count=%d size=%d" % (N, e['size']))

def uv(i):  return (struct.unpack_from('<i', vc.data, co+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', vc.data, co+0xDB18+i*4)[0])
def rec(i): return struct.unpack_from('<IIII', vc.data, co+0xD0+i*16)

print("\n改前:")
for dst, src in FIX.items():
    print("  vf3[%d] U/V=%s rec=%s   <- 将改成 src=%d 的 U/V=%s" %
          (dst, uv(dst), rec(dst), src, uv(src)))

if not os.path.exists(BAK):
    shutil.copy2(COMMON, BAK)
    print("\n✓ 备份 ->", BAK)
else:
    print("\n备份已存在 md5", hashlib.md5(open(BAK,'rb').read()).hexdigest())

for dst, src in FIX.items():
    u, v = uv(src)
    struct.pack_into('<i', vc.data, co+0xAF6C+dst*4, u)
    struct.pack_into('<i', vc.data, co+0xDB18+dst*4, v)
    struct.pack_into('<IIII', vc.data, co+0xD0+dst*16, *rec(src))

os.makedirs(os.path.dirname(OUT_C), exist_ok=True)
vc.save(OUT_C)
print("\n✓ 写出", OUT_C, "md5", hashlib.md5(open(OUT_C,'rb').read()).hexdigest())

# ---- 校验 ----
print("\n=== 校验 ===")
v2 = Vpp(OUT_C); e2 = v2.find("fnt_chinese","vf3_pc"); c2 = v2.data_start + e2['body']
def nUv(i): return (struct.unpack_from('<i', v2.data, c2+0xAF6C+i*4)[0],
                    struct.unpack_from('<i', v2.data, c2+0xDB18+i*4)[0])
ok = True
for dst, src in FIX.items():
    a, b = nUv(dst), nUv(src)
    good = (a == b); ok &= good
    print("  vf3[%d] = %s  目标=%s  %s" % (dst, a, b, "OK" if good else "★"))
print("三处字形修正正确:", ok)
assert ok
# 确认新槽(2288/2325/2616)两条路径未受影响
for nm, ns in (("徒",2288),("录",2325),("弹",2616)):
    print("  %s 新槽%d: 正常idx%d=%s 坏idx%d=%s (未动)" %
          (nm, ns, ns-0x20, nUv(ns-0x20), ns-0x40, nUv(ns-0x40)))
print("\n✓ common v421 构建完成")