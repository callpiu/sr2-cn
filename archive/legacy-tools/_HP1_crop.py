# -*- coding: utf-8 -*-
from PIL import Image
import os
D = r"D:\steam\userdata\313416396\760\remote\9480\screenshots"
jobs = [("20261016182128_1.jpg", (930,910,1720,1000), "_SUB1.png"),
        ("20261016182157_1.jpg", (760,910,1960,1000), "_SUB2.png")]
for fn, box, out in jobs:
    im = Image.open(os.path.join(D, fn)).convert("RGB")
    c = im.crop(box)
    c = c.resize((c.width*4, c.height*4), Image.LANCZOS)
    c.save(r"F:\sr2-cn\%s" % out)
    print(out, c.size)
