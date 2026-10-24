import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
M = cl(os.path.join(G,"patch.vpp_pc"))
# 官方 vf3 + 官方图集
vp = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
vf = vp.read(vp.find("fnt_chinese","vf3_pc"))
at = vp.read(vp.find("fnt_chinese","g_peg_pc"))
N = struct.unpack_from('<I', vf, 8)[0]
uo = 0xBC + N*16
U = [struct.unpack_from('<I', vf, uo+i*4)[0] for i in range(N)]
V = [struct.unpack_from('<I', vf, uo+N*4+i*4)[0] for i in range(N)]
_, A = dxt3_decode(at, 2048, 2048)
# 我的图集
gm = Vpp(os.path.join(G,"patch.vpp_pc"))
atm = gm.read(gm.find("fnt_chinese","g_peg_pc"))
_, AM = dxt3_decode(atm, 2048, 2048)
vfm = gm.read(gm.find("fnt_chinese","vf3_pc"))
Nm = struct.unpack_from('<I', vfm, 8)[0]
uom = 0xBC + Nm*16
Um = [struct.unpack_from('<I', vfm, uom+i*4)[0] for i in range(Nm)]
Vm = [struct.unpack_from('<I', vfm, uom+Nm*4+i*4)[0] for i in range(Nm)]
tests = [0,1,31,32,33,34,64,65,66,100]
SC = 4
rows = []
for g in tests:
    # 官方
    cO = A[V[g]:V[g]+31, U[g]:U[g]+31]
    cM = AM[Vm[g]:Vm[g]+31, Um[g]:Um[g]+31]
    chO = chr(O[g]) if g < len(O) else '?'
    chM = chr(M[g]) if g < len(Nm and M) and g < len(M) else '?'
    rows.append((g, chO, chM, cO, cM))
W = 2*31*SC + 40 + 2*200
H = len(rows)*31*SC + 30
canvas = np.full((H, W), 30, np.uint8)
im = Image.fromarray(canvas); d = ImageDraw.Draw(im)
y = 20
for g, chO, chM, cO, cM in rows:
    x = 10
    d.text((x, y-16), "OFFICIAL", fill=255); x = 10
    imgO = Image.fromarray(np.kron(cO, np.ones((SC,SC), np.uint8)))
    im.paste(imgO, (x, y))
    d.text((x+31*SC+4, y+8), "vf3[%d]  charlist_O[%d]=%s" % (g, g, chO), fill=255)
    x = 10 + 31*SC + 4 + 210
    d.text((x, y-16), "MINE", fill=255)
    imgM = Image.fromarray(np.kron(cM, np.ones((SC,SC), np.uint8)))
    im.paste(imgM, (x, y))
    d.text((x+31*SC+4, y+8), "vf3[%d]  charlist_M[%d]=%s" % (g, g, chM), fill=255)
    y += 31*SC + 14
im.save(r"F:\sr2-cn\_EJ1_final_ab.png")
print("saved _EJ1_final_ab.png")
for g, chO, chM, cO, cM in rows:
    print("  vf3[%3d]: official cell ink=%5d (charlist_O=%s) | mine cell ink=%5d (charlist_M=%s)"
          % (g, int((cO>0).sum()), chO, int((cM>0).sum()), chM))
