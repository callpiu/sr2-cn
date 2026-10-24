# -*- coding: utf-8 -*-
"""★★★ 最终验收：按引擎真实路径（common.vf3 + textures 图集 + charlist 索引）渲染"""
import sys, os, struct, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 当前部署状态 ===")
for f in ("common.vpp_pc", "patch.vpp_pc", "textures.vpp_pc"):
    p = os.path.join(G, f)
    h = hashlib.md5()
    with open(p, 'rb') as fp:
        for b in iter(lambda: fp.read(1 << 22), b''):
            h.update(b)
    print("  %-16s %12d  md5 %s" % (f, os.path.getsize(p), h.hexdigest()))

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)
print("\ncharlist_CH = %d 条" % len(CL))

vc = Vpp(os.path.join(G, "common.vpp_pc"))
ec = vc.find("fnt_chinese", "vf3_pc")
o = vc.data_start + ec['body']
N = struct.unpack_from('<I', vc.data, o + 8)[0]
uo = 0xBC + N*16; vo = uo + N*4
U = [struct.unpack_from('<I', vc.data, o+uo+i*4)[0] for i in range(N)]
V = [struct.unpack_from('<I', vc.data, o+vo+i*4)[0] for i in range(N)]
print("引擎 vf3 (common): N=%d  size=%d  md5=%s" % (
    N, ec['size'], hashlib.md5(vc.read(ec)).hexdigest()))

vt = Vpp(os.path.join(G, "textures.vpp_pc"))
et = next(x for x in vt.entries() if x['name'] == 'fnt_chinese')
AT = vt.read(et)
print("引擎图集 (textures): size=%d md5=%s" % (len(AT), hashlib.md5(AT).hexdigest()))
_, A = dxt3_decode(AT, 2048, 2048)

TEXT = "你的弟兄们需要你的保护"
idx = [c2i[c] for c in TEXT]
imgs = []
for s in idx:
    u, vv = U[s], V[s]
    imgs.append(A[vv:vv+32, u:u+32])
strip = np.hstack([np.pad(x, ((2,2),(2,2))) for x in imgs])
Image.fromarray(np.kron(strip, np.ones((2,2), 'uint8'))).save(
    r"F:\sr2-cn\_FINAL_rec1.png")
print("\n★ 渲染 '%s' 用 idx=%s" % (TEXT, idx))
print("  写出 _FINAL_rec1.png")

# REC2
TEXT2 = "要出去谈几笔生意，保护他们免遭袭击"
idx2 = [c2i.get(c) for c in TEXT2]
miss = [c for c, i in zip(TEXT2, idx2) if i is None]
print("\nREC2 '%s'" % TEXT2)
print("  字表中缺失:", miss if miss else "无")
imgs2 = []
for s in idx2:
    if s is None:
        imgs2.append(np.zeros((32, 32), 'uint8')); continue
    u, vv = U[s], V[s]
    imgs2.append(A[vv:vv+32, u:u+32])
strip2 = np.hstack([np.pad(x, ((2,2),(2,2))) for x in imgs2])
Image.fromarray(np.kron(strip2, np.ones((2,2), 'uint8'))).save(
    r"F:\sr2-cn\_FINAL_rec2.png")
print("  写出 _FINAL_rec2.png")

# 对照：修复前的 common vf3
bak = r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc"
vb = Vpp(bak)
eb = vb.find("fnt_chinese", "vf3_pc")
ob = vb.data_start + eb['body']
Nb = struct.unpack_from('<I', vb.data, ob + 8)[0]
uob = 0xBC + Nb*16; vob = uob + Nb*4
Ub = [struct.unpack_from('<I', vb.data, ob+uob+i*4)[0] for i in range(Nb)]
Vb = [struct.unpack_from('<I', vb.data, ob+vob+i*4)[0] for i in range(Nb)]
imgsb = [A[Vb[s]:Vb[s]+32, Ub[s]:Ub[s]+32] for s in idx]
stripb = np.hstack([np.pad(x, ((2,2),(2,2))) for x in imgsb])
Image.fromarray(np.kron(stripb, np.ones((2,2), 'uint8'))).save(
    r"F:\sr2-cn\_BEFORE_rec1.png")
print("\n  写出 _BEFORE_rec1.png（修复前，同一图集）")

W = max(strip.shape[1], stripb.shape[1])
cv = np.zeros((strip.shape[0]+stripb.shape[0]+10, W), 'uint8')
cv[:stripb.shape[0], :stripb.shape[1]] = stripb
cv[stripb.shape[0]+10:, :strip.shape[1]] = strip
Image.fromarray(cv).save(r"F:\sr2-cn\_FINAL_compare.png")
print("  写出 _FINAL_compare.png（上=修复前 下=修复后）")
