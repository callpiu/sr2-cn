import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "textures.vpp_pc"))
raw = v.read(v.find("fnt_body_n"))
print("fnt_body_n atlas size =", len(raw), "md5 =", hashlib.md5(raw).hexdigest()[:12])
rgb, alpha = dxt3_decode(raw, 2048, 2048)

# cells for 你的弟兄们需要你的保护 -> slots 371,1836,1035,422,332,2667,2296,371,1836,391,1190
SLOTS = [371, 1836, 1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]
def cell(i):
    return alpha[1+31*(i//65): 1+31*(i//65)+31, 1+31*(i%65): 1+31*(i%65)+31]
row = np.concatenate([cell(i) for i in SLOTS], axis=1)
img = np.kron(row, np.ones((6, 6), np.uint8))
Image.fromarray(img, "L").save(r"F:\sr2-cn\_GB4_verify.png")
print("saved _GB4_verify.png", img.shape)

# also check the pegs descriptor now
p = Vpp(os.path.join(G, "pegs.vpp_pc"))
import struct
d = p.read(p.find("fnt_body_n"))
print("pegs fnt_body_n: dataSize=%d w=%d h=%d fmt=%d" % (
    struct.unpack_from("<I", d, 12)[0], *struct.unpack_from("<HH", d, 28),
    struct.unpack_from("<I", d, 32)[0]))
