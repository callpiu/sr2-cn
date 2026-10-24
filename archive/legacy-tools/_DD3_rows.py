import numpy as np
from collections import Counter
b = open(r"F:/sr2-cn/_fontdump/vf3_offi.bin","rb").read()
N=2838; H=0xBC; o=H+N*16
U = np.frombuffer(b,dtype="<u4",count=N,offset=o)
V = np.frombuffer(b,dtype="<u4",count=N,offset=o+N*4)
# 每个 V 行有多少字形、U 是否跨行复用
rows = {}
for i in range(N):
    rows.setdefault(int(V[i]), []).append(int(U[i]))
print("官方: 共 %d 行, 每行字形数分布 %s" % (len(rows), Counter(len(v) for v in rows.values()).most_common(6)))
for r in list(sorted(rows))[:4]:
    u = sorted(rows[r])
    print("  V=%4d  n=%3d  U前14=%s" % (r, len(u), u[:14]))
    print("           间距=%s" % Counter([u[i+1]-u[i] for i in range(len(u)-1)]).most_common(6))
# 同一 U 是否出现在多行
uu = Counter(U.tolist())
print("U 出现次数分布:", Counter(uu.values()).most_common(6))
print()
# 我方 vf3 同项
b2 = open(r"F:/sr2-cn/_fontdump/fnt_chinese.vf3_pc","rb").read()
N2=2795; o2=H+N2*16
U2 = np.frombuffer(b2,dtype="<u4",count=N2,offset=o2)
V2 = np.frombuffer(b2,dtype="<u4",count=N2,offset=o2+N2*4)
r2={}
for i in range(N2): r2.setdefault(int(V2[i]),[]).append(int(U2[i]))
print("我方: 共 %d 行, 每行字形数 %s" % (len(r2), Counter(len(v) for v in r2.values()).most_common(4)))
for r in list(sorted(r2))[:3]:
    u=sorted(r2[r]); print("  V=%4d n=%3d U前10=%s" % (r,len(u),u[:10]))
