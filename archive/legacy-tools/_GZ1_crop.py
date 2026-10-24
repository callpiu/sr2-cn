from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
jobs = [("20261016182128_1.jpg", (400, 425, 700, 465)),
        ("20261016182157_1.jpg", (300, 425, 800, 465))]
for i,(fn, box) in enumerate(jobs, 1):
    im = Image.open(os.path.join(S, fn))
    print(fn, im.size)
    c = im.crop(box)
    c = c.resize((c.width*5, c.height*5), Image.LANCZOS)
    out = rf"F:/sr2-cn/_ZZ_garb{i}.png"
    c.save(out)
    print("saved", out, c.size)
