import numpy as np
RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
a = np.fromfile(RAW, dtype=np.uint8).reshape(2048, 2048)

def show(y0, y1, x0, x1, thr=110):
    print("--- y %d..%d  x %d..%d (thr=%d) ---" % (y0, y1, x0, x1, thr))
    hdr = "     " + "".join(str((x // 10) % 10) for x in range(x0, x1))
    print(hdr)
    print("     " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        row = "".join("#" if a[y, x] > thr else "." for x in range(x0, x1))
        print("%4d %s" % (y, row))

show(8, 32, 0, 64)
show(8, 32, 0, 34, 60)
