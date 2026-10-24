from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
im = Image.open(os.path.join(S, "20261016182128_1.jpg"))
c = im.crop((1045, 912, 1565, 962)); c = c.resize((c.width*6, c.height*6), Image.LANCZOS)
c.save(r"F:/sr2-cn/_ZZ_t1.png"); print(c.size)
im2 = Image.open(os.path.join(S, "20261016182157_1.jpg"))
c2 = im2.crop((0, 820, 2560, 1050)); c2 = c2.resize((c2.width//2, c2.height//2), Image.LANCZOS)
c2.save(r"F:/sr2-cn/_ZZ_b2.png"); print(c2.size)
