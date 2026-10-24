import struct, numpy as np
b = open(r"F:/sr2-cn/_fontdump/vf3_offi.bin","rb").read()
N=2838; H=0xBC; o16=H+N*16
U = np.frombuffer(b,dtype="<u4",count=N,offset=o16)
V = np.frombuffer(b,dtype="<u4",count=N,offset=o16+N*4)
recs=[struct.unpack_from("<IIII",b,H+i*16) for i in range(N)]
print("官方 vf3 前 40 个字形记录 {w,h,?,?}:")
for i in range(40):
    print("  [%3d] w=%3d h=%3d c=%d d=%d   U=%4d V=%4d" % (i, recs[i][0], recs[i][1], recs[i][2], recs[i][3], U[i], V[i]))
z=[i for i in range(N) if recs[i][0]==0 and recs[i][1]==0]
print("\nw=h=0 的字形数:", len(z), " 前 40 个:", z[:40])
print("w=0 的个数:", sum(1 for r in recs if r[0]==0), "  h=0 的个数:", sum(1 for r in recs if r[1]==0))
print("\n第 0..5 行(V=1,32,63)的首个非零记录位置:")
seen=0
for i in range(N):
    if recs[i][0] or recs[i][1]:
        print("  首个非零记录 idx=%d" % i); break
# 我方
b2 = open(r"F:/sr2-cn/_fontdump/fnt_chinese.vf3_pc","rb").read()
N2=2795
r2=[struct.unpack_from("<IIII",b2,H+i*16) for i in range(N2)]
print("\n我方 vf3 N=%d, w=h=0 的字形数: %d" % (N2, sum(1 for r in r2 if r[0]==0 and r[1]==0)))
print("我方前 6 个记录:", [(r[0],r[1]) for r in r2[:6]])
