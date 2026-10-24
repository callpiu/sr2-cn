import numpy as np, os
from PIL import Image
p = r"C:\Users\ezplayer\.dsh\attachments\v1\objects\40\407c1adcae3c46165a5af89082c1561f1b7fc91d3edcce074be2612f1782accd"
imc = np.asarray(Image.open(p).convert("RGB")).astype(int)
r,g,b = imc[:,:,0], imc[:,:,1], imc[:,:,2]
blue = (b > 110) & (b - r > 40) & (b - g > 25)
# 只取标题行区域
sub = blue[429:460, 700:1120]
rows = np.nonzero(sub.any(axis=1))[0]
print("标题行: 墨迹占 %d 行 (即字形高度约 %d 像素)" % (len(rows), rows.max()-rows.min()+1))
# 中文行「选项」等看高度作为对照（白色文字）
white = (r>190)&(g>190)&(b>190)
# 找底部按钮「接受 恢复默认 返回」那行
print()
# 逐字符块的高度
band = blue[429:460, :]
cols = np.nonzero(band.any(axis=0))[0]
blocks=[]; inb=False
for x in range(imc.shape[1]):
    c = band[:,x].any()
    if c and not inb: inb=True; st=x
    elif not c and inb: inb=False; blocks.append((st,x-1))
print("各块高度:")
for i,(a,bb) in enumerate(blocks):
    seg = band[:, a:bb+1]
    ys = np.nonzero(seg.any(axis=1))[0]
    print("  #%-3d x %4d..%4d 宽%2d  高%2d (行 %d..%d)" % (i,a,bb,bb-a+1,len(ys),ys.min(),ys.max()))
