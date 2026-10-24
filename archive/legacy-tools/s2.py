import numpy as np
from PIL import Image
p = r"C:\Users\ezplayer\.dsh\attachments\v1\objects\65\65ccd2ea39d02ccf92ec4c3cfcdbd8fbe15dd5749c96156a73a9a8b8e47bf2e5"
imc = np.asarray(Image.open(p).convert("RGB")).astype(int)
r,g,b = imc[:,:,0], imc[:,:,1], imc[:,:,2]
# 找各行文字（非背景）
lum = (r+g+b)/3
print("截图 %s" % (lum.shape,))
# Juice 菜单位置：左侧 x 200..800, y 240..820
sub = lum[240:830, 190:820]
# 逐行统计亮点
rowink = (sub > 70).sum(axis=1)
print("左侧标签区每 20 行的亮点数:")
for y0 in range(0, sub.shape[0], 20):
    seg = rowink[y0:y0+20]
    print("  y %3d..%3d : %5d" % (y0+240, y0+260, int(seg.sum())))
