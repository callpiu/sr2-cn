import numpy as np
from PIL import Image
p = r"C:\Users\ezplayer\.dsh\attachments\v1\objects\65\65ccd2ea39d02ccf92ec4c3cfcdbd8fbe15dd5749c96156a73a9a8b8e47bf2e5"
im = Image.open(p).convert("L")
A = np.asarray(im).astype(int)
print("=== 逐条菜单行的亮度统计（左侧标签列 x 190..820）===")
sub = A[:, 190:820]
for y0 in range(255, 830, 23):
    seg = sub[y0:y0+22]
    mx = int(seg.max()); mean = float(seg.mean()); n70 = int((seg>70).sum())
    print("  y %3d..%3d  max %3d  mean %5.1f  >70:%4d" % (y0, y0+21, mx, mean, n70))
