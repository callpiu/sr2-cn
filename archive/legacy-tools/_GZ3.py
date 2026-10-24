from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
im = Image.open(os.path.join(S, "20261016182128_1.jpg"))
c = im.crop((0, 850, 2560, 1250))
c = c.resize((c.width//2, c.height//2), Image.LANCZOS)
c.save(r"F:/sr2-cn/_ZZ_band1.png")
print(c.size)
im2 = Image.open(os.path.join(S, "20261016182157_1.jpg"))
c2 = im2.crop((0, 800, 2560, 1200))
c2 = c2.resize((c2.width//2, c2.height//2), Image.LANCZOS)
c2.save(r"F:/sr2-cn/_ZZ_band2.png")
print(c2.size)
