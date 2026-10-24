"""渲染图集A(patch) vs 图集B(textures) 的 idx 1000~1110 cell，对照 charlist 看错位。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_atlas(path, container):
    vv = Vpp(path)
    e = None
    for ent in vv.entries():
        if ent['name'].lower() == 'fnt_chinese' and ent['size'] >= 2097152:
            e = ent
            print("%s: 用条目 %s ext=%r size=%d" % (container, ent['name'], ent['ext'], ent['size']))
            break
    rgb, a = dxt3_decode(vv.read(e), 2048, 2048)
    try:
        vf3 = bytes(vv.read(vv.find("fnt_chinese", "vf3_pc")))
    except Exception:
        vcom = Vpp(os.path.join(GAME, "common.vpp_pc"))
        vf3 = bytes(vcom.read(vcom.find("fnt_chinese", "vf3_pc")))
    n3 = struct.unpack_from('<i', vf3, 0x08)[0]
    U = list(struct.unpack_from('<%di' % n3, vf3, 0xAF6C))
    V = list(struct.unpack_from('<%di' % n3, vf3, 0xDB18))
    return a, U, V

e_cl = v = None
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8','replace').split() if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if (nums and nums[0]==len(nums)-1) else nums

aA, UA, VA = load_atlas(os.path.join(GAME, "patch.vpp_pc"), "patch")
aB, UB, VB = load_atlas(os.path.join(GAME, "textures.vpp_pc"), "textures")
print("图集B vf3 N =", len(UB))

# 渲染 idx 990~1110 两行对照条：每行 = charlist 应有字 + 图集A cell + 图集B cell
IDX0, IDX1 = 990, 1110
CELL = 30
cols = 20
rows = (IDX1 - IDX0 + cols - 1) // cols
SCALE = 2
W = cols * (CELL + 14) * SCALE
H = rows * (CELL * 3 + 22) * SCALE
img = Image.new("L", (W, H), 255)
dr = ImageDraw.Draw(img)

def paste_cell(arr, u, vv_, x, y):
    cell = arr[vv_:vv_+CELL, u:u+CELL]
    im = Image.fromarray(cell)
    im = im.resize((CELL*SCALE, CELL*SCALE), Image.NEAREST)
    img.paste(im, (x, y))

for k, i in enumerate(range(IDX0, IDX1)):
    r, c = divmod(k, cols)
    x0 = c * (CELL + 14) * SCALE
    y0 = r * (CELL * 3 + 22) * SCALE
    ch = chr(cl[i])
    dr.text((x0, y0), "%d %s" % (i, ch), fill=0)
    paste_cell(aA, UA[i], VA[i], x0, y0 + 12 * SCALE)          # 图集A
    if i < len(UB):
        paste_cell(aB, UB[i], VB[i], x0 + (CELL+7)*SCALE, y0 + 12*SCALE)  # 图集B
    dr.text((x0, y0 + (12+CELL)*SCALE), "A|B", fill=0)

img.save(r"F:\sr2-cn\_juice_fix\v418_atlas_cmp_990_1110.png")
print("saved v418_atlas_cmp_990_1110.png")

# 数值层面：图集A直接量 cell 墨迹，与图集B一致性统计
import numpy as np
same = diff = 0
for i in range(0, min(len(UB), len(UA))):
    ca = aA[VA[i]:VA[i]+CELL, UA[i]:UA[i]+CELL]
    cb = aB[VB[i]:VB[i]+CELL, UB[i]:UB[i]+CELL]
    if ca.shape != cb.shape: continue
    if np.array_equal(ca, cb): same += 1
    else: diff += 1
print("全表 cell 一致: %d  不同: %d" % (same, diff))
