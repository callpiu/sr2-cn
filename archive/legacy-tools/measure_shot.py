import numpy as np
from PIL import Image
p = r"C:\Users\ezplayer\.dsh\attachments\v1\objects\40\407c1adcae3c46165a5af89082c1561f1b7fc91d3edcce074be2612f1782accd"
im = Image.open(p).convert("L")
A = np.asarray(im).astype(int)
print("截图 %s" % (A.shape,))
# 蓝色标题行「Display & Audio Options」大约在 y=290..310（1708 宽的预览对应 2560 实图）
# 先找蓝色像素
imc = np.asarray(Image.open(p).convert("RGB")).astype(int)
r,g,b = imc[:,:,0], imc[:,:,1], imc[:,:,2]
blue = (b > 110) & (b - r > 40) & (b - g > 25)
ys, xs = np.nonzero(blue)
print("蓝色像素 %d 个, y 范围 %d..%d, x 范围 %d..%d" % (len(ys), ys.min(), ys.max(), xs.min(), xs.max()))
# 只取标题行
if len(ys):
    y0,y1 = ys.min(), ys.max()
    band = blue[y0:y1+1, :]
    cols = np.nonzero(band.any(axis=0))[0]
    # 找连续块
    blocks=[]; inb=False
    for x in range(A.shape[1]):
        c = x in set(cols.tolist())
        if c and not inb: inb=True; st=x
        elif not c and inb: inb=False; blocks.append((st,x-1))
    if inb: blocks.append((st,A.shape[1]-1))
    print()
    print("标题行检测到 %d 个字符块:" % len(blocks))
    for i,(a,b) in enumerate(blocks):
        print("  #%-3d x %4d..%4d 宽 %2d" % (i,a,b,b-a+1))
    if len(blocks) > 1:
        steps=[blocks[i+1][0]-blocks[i][0] for i in range(len(blocks)-1)]
        print()
        print("字符步进: %s" % steps)
        print("步进中位数: %.1f" % float(np.median(steps)))
