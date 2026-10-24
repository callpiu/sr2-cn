from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
im = Image.open(os.path.join(S, "20261016182128_1.jpg"))
c = im.crop((1040, 895, 1560, 965)); c = c.resize((c.width*6, c.height*6), Image.LANCZOS)
c.save(r"F:/sr2-cn/_ZZ_txt1.png"); print(c.size)
