import numpy as np
from PIL import Image
for tag, p in (("Option1", r"C:\Users\ezplayer\.dsh\attachments\v1\objects\b7\b7611698161f567e8acb4c75ab77703b8884b028b1e02eff1fddbeef16a2e3ef"),
               ("Option2", r"C:\Users\ezplayer\.dsh\attachments\v1\objects\92\927c4e536d4606ea8cacad6a788916f7a3612f595a3da3815c45a70f769f0f4")):
    try:
        A = np.asarray(Image.open(p).convert("L")).astype(int)
    except Exception as e:
        print("  %s 打不开: %s" % (tag, e)); continue
    print("=== %s ===" % tag)
    # 左侧标签列
    sub = A[:, 470:1200]
    for y0 in range(240, 830, 24):
        seg = sub[y0:y0+23]
        print("  y %3d..%3d  max %3d  >75:%5d" % (y0, y0+22, int(seg.max()), int((seg>75).sum())))
    print()
