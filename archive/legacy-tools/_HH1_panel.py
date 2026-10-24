from PIL import Image
import os
S = r"D:/steam/userdata/313416396/760/remote/9480/screenshots"
im = Image.open(os.path.join(S, "20261016182157_1.jpg"))
print("size", im.size)
c = im.crop((200, 90, 1050, 340)); c = c.resize((c.width*2, c.height*2), Image.LANCZOS)
c.save(r"F:/sr2-cn/_ZZ_panel.png"); print(c.size)
