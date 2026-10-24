import sys, os, struct
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
vo = Vpp(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
vf = vo.read(vo.find("fnt_chinese","vf3_pc"))
at = vo.read(vo.find("fnt_chinese","g_peg_pc"))
cl = vo.read(vo.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
nums = [int(s) for s in cl if s.strip().isdigit()]
N=struct.unpack_from('<I',vf,8)[0]; uo=0xBC+N*16
U=[struct.unpack_from('<I',vf,uo+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<I',vf,uo+N*4+i*4)[0] for i in range(N)]
_,A = dxt3_decode(at,2048,2048)
def cell(g): return A[V[g]:V[g]+31, U[g]:U[g]+31]
tests = [("'A'码点65  charlist_idx=33", 33), ("compressed=33+32=65", 65),
         ("'B'码点66  charlist_idx=34", 34), ("compressed=34+32=66", 66),
         ("'0'码点48  charlist_idx=16", 16), ("compressed=16+32=48", 48)]
imgs=[]; labels=[]
for lab,g in tests:
    c=cell(g)
    imgs.append(np.pad(np.kron(c,np.ones((3,3),'uint8')),((2,2),(2,2)),constant_values=40))
    labels.append(lab)
W=sum(x.shape[1] for x in imgs)
canvas=np.zeros((len(imgs)*100+40, W),'uint8'); y=0
for x in imgs:
    canvas[y:y+x.shape[0], 0:x.shape[1]]=x; y+=x.shape[0]+2
im=Image.fromarray(canvas); d=ImageDraw.Draw(im)
y=0
for lab,x in zip(labels,imgs):
    d.text((3,y+2), "%s   ->下方字" % lab, fill=255); y+=x.shape[0]+2
im.save(r"F:/sr2-cn/_DR1_ab.png")
print("已生成 _DR1_ab.png : 每段标注了它是 charlist 位置还是 +32 后的 compressed 号")
for lab,g in tests:
    v=nums[g] if g<len(nums) else None
    print("   %-34s vf3[%4d] -> codepoint %s (%s)" % (lab,g,v,chr(v) if v and 32<=v<0x30000 else '?'))
