"""决定性验证：图集B(common vf3 UV) 在 idx 1009~1075 的字形内容。
   若 B[k] 画的是我们表 charlist[k-32] 的字 => 短文本路径=B体系 实锤。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
nums = [int(x) for x in v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').split() if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0]==len(nums)-1) else nums

vcom = Vpp(os.path.join(GAME, "common.vpp_pc"))
vf3 = bytes(vcom.read(vcom.find("fnt_chinese","vf3_pc")))
n3 = struct.unpack_from('<i', vf3, 0x08)[0]
print("common vf3 N =", n3, " len =", len(vf3))
# 定位 U/V 数组: 假设结构与 patch 相同 (头0xD0 + N*16 + U + V)
# patch: U@0xAF6C = 0xD0+2795*16-4? 实测 0xAF6C=44908; 0xD0+2795*16=44928. 差20。直接搜索特征。
# 更稳: 尝试多个候选起点，找 U 序列单调(步长≈31) 且 V 单调的
def find_uv(vf3, n3):
    base = 0xD0 + n3*16
    best = None
    for du in range(-64, 256, 4):
        u0 = base + du
        if u0 < 0 or u0 + n3*8 > len(vf3): continue
        U = list(struct.unpack_from('<%di'%n3, vf3, u0))
        V = list(struct.unpack_from('<%di'%n3, vf3, u0+n3*4))
        # 校验: U 大体 0..2047 单调分段, V 大体 0..2047 单调
        try:
            oku = all(-4<=U[i+1]-U[i]<=64 for i in range(0, 2000)) and 0<=U[0]<100
            okv = all(0<=V[i]<=2100 for i in range(0, n3)) and V[0]<=V[n3//2]<=V[-1]
            if oku and okv:
                best = (u0, U, V); break
        except Exception:
            continue
    return best

u0, UB, VB = find_uv(vf3, n3)
print("common vf3 U@0x%X (patch=0xAF6C)" % (u0 or 0))
if UB is None:
    # 直接用与 patch 相同的偏移
    UB = list(struct.unpack_from('<%di'%n3, vf3, 0xAF6C))
    VB = list(struct.unpack_from('<%di'%n3, vf3, 0xAF6C + n3*4))
    print("回退: 用 patch 同款偏移")

vtex = Vpp(os.path.join(GAME, "textures.vpp_pc"))
eB = [e for e in vtex.entries() if e['name'].lower()=='fnt_chinese'][0]
rgb, aB = dxt3_decode(vtex.read(eB), 2048, 2048)

# patch 体系 UV 供对照
vf3p = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
UP = list(struct.unpack_from('<%di'%2795, vf3p, 0xAF6C))
VP = list(struct.unpack_from('<%di'%2795, vf3p, 0xDB18))
eA = v.find("fnt_chinese","g_peg_pc")
rgb, aA = dxt3_decode(v.read(eA), 2048, 2048)

IDX0, IDX1 = 1005, 1076
CELL = 30
SCALE = 3
cols = 12
import math
rows = math.ceil((IDX1-IDX0)/cols)
CW = (CELL+6)*SCALE
img = Image.new("L", (cols*CW, rows*(CELL*3+30)*SCALE), 255)
dr = ImageDraw.Draw(img)
for k, i in enumerate(range(IDX0, IDX1)):
    r, c = divmod(k, cols)
    x0 = c*CW; y0 = r*(CELL*3+30)*SCALE//SCALE*SCALE
    y0 = r*(CELL*3+30)*SCALE
    ch = chr(cl[i])
    chB = chr(cl[i-32]) if i>=32 else '?'
    dr.text((x0, y0), "%d:%s/%s" % (i, ch, chB), fill=0)
    # A: patch UV[i]
    ca = aA[VP[i]:VP[i]+CELL, UP[i]:UP[i]+CELL]
    im = Image.fromarray(ca).resize((CELL*SCALE, CELL*SCALE), Image.NEAREST)
    img.paste(im, (x0, y0+14*SCALE))
    # B: common UV[i]
    cb = aB[VB[i]:VB[i]+CELL, UB[i]:UB[i]+CELL]
    im = Image.fromarray(cb).resize((CELL*SCALE, CELL*SCALE), Image.NEAREST)
    img.paste(im, (x0+(CELL+3)*SCALE, y0+14*SCALE))
img.save(r"F:\sr2-cn\_juice_fix\v418_B_verify.png")
print("saved v418_B_verify.png  (每格: idx:我们表字/B体系若-32应显示的字, 左=A[我们UV], 右=B[commonUV同idx])")
