import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
def get(p,n,e):
    v=Vpp(p); return v.read(v.find(n,e))
vf = get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig","fnt_chinese","vf3_pc")
N = struct.unpack_from('<I', vf, 8)[0]
uo = 0xBC + N*16
U = [struct.unpack_from('<I', vf, uo+i*4)[0] for i in range(N)]
V = [struct.unpack_from('<I', vf, uo+N*4+i*4)[0] for i in range(N)]
print("official N=%d" % N)
uu = sorted(set(U)); vv = sorted(set(V))
print("U unique=%d  V unique=%d" % (len(uu), len(vv)))
print("U 前14:", uu[:14])
print("U 间距:", [uu[i+1]-uu[i] for i in range(min(13,len(uu)-1))])
print("V 前10:", vv[:10])
print("V 间距:", [vv[i+1]-vv[i] for i in range(min(9,len(vv)-1))])
print()
# 试各种列数: U == start+step*(i%cols)?
best=[]
for cols in (64,65,66,67,68):
    for step in (31,32):
        for start in (1,0):
            okU = sum(1 for i in range(N) if U[i]==start+step*(i%cols))
            okV = sum(1 for i in range(N) if V[i]==start+step*(i//cols))
            best.append((okU+okV, cols, step, start, okU, okV))
best.sort(reverse=True)
for tot,cols,step,start,okU,okV in best[:6]:
    print("cols=%d step=%d start=%d -> U命中 %d/%d (%.1f%%)  V命中 %d/%d (%.1f%%)"
          % (cols,step,start,okU,N,100*okU/N,okV,N,100*okV/N))
print()
# 按行看官方每行多少字形
rows={}
for i in range(N): rows.setdefault(V[i],[]).append(i)
from collections import Counter
print("官方行数:", len(rows))
print("每行字形数:", Counter(len(v) for v in rows.values()).most_common(6))
for r in sorted(rows)[:3]:
    us=sorted(U[i] for i in rows[r])
    print("  V=%d: %d 字形, U前12=%s" % (r, len(rows[r]), us[:12]))
