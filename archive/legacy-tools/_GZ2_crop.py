from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
jobs = [("20261016182128_1.jpg", (940, 1000, 1650, 1100)),
        ("20261016182157_1.jpg", (700, 890, 1750, 1000))]
for i,(fn, box) in enumerate(jobs, 1):
    im = Image.open(os.path.join(S, fn))
    c = im.crop(box)
    c = c.resize((c.width*3, c.height*3), Image.LANCZOS)
    out = rf"F:/sr2-cn/_ZZ_garb{i}.png"
    c.save(out)
    print("saved", out, c.size)
