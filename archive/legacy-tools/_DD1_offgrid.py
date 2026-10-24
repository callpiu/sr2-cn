import numpy as np
b = open(r"F:/sr2-cn/_fontdump/vf3_offi.bin","rb").read()
N = 2838
H = 0xBC
print("len", len(b), "expect", H + N*16 + N*4 + N*4)
o16 = H + N*16
U = np.frombuffer(b, dtype="<u4", count=N, offset=o16)
V = np.frombuffer(b, dtype="<u4", count=N, offset=o16 + N*4)
print("U[:12]", U[:12].tolist())
print("V[:12]", V[:12].tolist())
print("U uniq", len(set(U.tolist())), "V uniq", len(set(V.tolist())))
print("U min/max", U.min(), U.max(), "V min/max", V.min(), V.max())
# 试各种 (列数, 行距, 列距, 起点)
for cols in (60,62,64,65,66,67,68,70):
    for step in (31,32,30):
        for start in (0,1):
            okU = okV = 0
            for i in range(N):
                if U[i] == start + step*(i % cols): okU += 1
                if V[i] == start + step*(i // cols): okV += 1
            if okU > N*0.5 or okV > N*0.5:
                print("cols=%d step=%d start=%d -> U %d/%d  V %d/%d" % (cols, step, start, okU, N, okV, N))
