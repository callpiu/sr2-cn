"""实证1: patch vf3 的 U/V 坐标在 idx 1000~1110 是否错一行（-64px）
   实证2: 渲染图集A对应 cell 看内容到底是谁的字形
   顺带: 解析 juiced_CH.le_strings 全部记录 + juiced_CH.cxt 搜 OpenSpy/胞胎/登录
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))

e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8','replace').split() if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0]==len(nums)-1) else nums
N = len(cl)
print("charlist N =", N)

# ---- vf3 解析（用已验证的正确起点）----
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
n3 = struct.unpack_from('<i', vf3, 0x08)[0]
print("vf3 N =", n3, " len =", len(vf3))
# 记忆: U@0xAF6C V@0xDB18 各N项 —— 校验: 0xDB18-0xAF6C = 0x2BAC = 11180 = 2795*4 ✓ (N=2795)
U = list(struct.unpack_from('<%di'%n3, vf3, 0xAF6C))
V = list(struct.unpack_from('<%di'%n3, vf3, 0xDB18))
print("U[0:6]", U[:6], " V[0:6]", V[:6])

# 预期网格: cell 31px + 1 节距 = 32; 64 cells/row
CELLP = 32
print("\n== idx 1000~1110 V 坐标 vs 预期 (idx//64)*32 ==")
bad_rows = {}
for i in range(1000, min(1110, n3)):
    exp_v = (i // 64) * CELLP
    exp_v_up = ((i - 64) // 64) * CELLP  # 上一行
    row, col = i // 64, i % 64
    # 实际 U 是否匹配 col*32?
    exp_u = col * CELLP
    tag = ""
    if V[i] == exp_v and U[i] == exp_u: tag = "OK"
    elif V[i] == exp_v - CELLP: tag = "V-1行 <<<"
    elif U[i] == exp_u - CELLP: tag = "U-1列"
    else: tag = "V=%d U=%d (exp %d,%d)" % (V[i], U[i], exp_v, exp_u)
    ch = chr(cl[i])
    print("  idx%4d '%s' row%2d col%2d  U=%4d V=%4d  %s" % (i, ch, row, col, U[i], V[i], tag))

# 统计整个表的 V 错行情况
print("\n== 全表 V 错行统计 ==")
err = {}
for i in range(n3):
    exp_v = (i // 64) * CELLP
    d = V[i] - exp_v
    if d != 0:
        err.setdefault(d // CELLP if d % CELLP == 0 else d, []).append(i)
for k, idxs in sorted(err.items(), key=lambda x: -len(x[1])):
    if isinstance(k, int) and abs(k) <= 4:
        rng = "idx %d~%d" % (min(idxs), max(idxs)) if len(idxs) > 1 else "idx %d" % idxs[0]
        # 是否连续
        cont = len(idxs) == max(idxs)-min(idxs)+1
        print("  V偏%+d行: %d 项 (%s, 连续=%s)" % (k, len(idxs), rng, cont))
    else:
        print("  其他偏移 %s: %d 项 (idx %d~%d)" % (k, len(idxs), min(idxs), max(idxs)))

# U 错列统计
print("\n== 全表 U 错列统计 ==")
erru = {}
for i in range(n3):
    exp_u = (i % 64) * CELLP
    d = U[i] - exp_u
    if d != 0:
        erru.setdefault(d, []).append(i)
for k, idxs in sorted(erru.items(), key=lambda x: -len(x[1])):
    print("  U偏%+d: %d 项 (idx %d~%d)" % (k, len(idxs), min(idxs), max(idxs)))
