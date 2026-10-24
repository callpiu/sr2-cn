from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
im2 = Image.open(os.path.join(S, "20261016182157_1.jpg"))
c2 = im2.crop((780, 935, 1820, 1000)); c2 = c2.resize((c2.width*5, c2.height*5), Image.LANCZOS)
c2.save(r"F:/sr2-cn/_ZZ_t2.png"); print(c2.size)
