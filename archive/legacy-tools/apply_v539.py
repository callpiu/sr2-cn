import struct, hashlib, sys

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
BASE = '27c3375d2f239d2da9bab49eead6cc5d'  # v538
buf = bytearray(open(P, 'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest() == BASE, 'baseline mismatch'

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def S(w):
    return struct.pack('>H', CL.index(ord(w)) + 0x20)

OLD = S('神') + S('父')   # 神父  (Father 被误译)
NEW = S('父') + S('亲')   # 父亲
assert len(OLD) == len(NEW)
assert buf.count(OLD) == 4, buf.count(OLD)
assert buf.count(NEW) == 16

out = bytes(buf).replace(OLD, NEW)
assert len(out) == len(buf), 'size changed!'
assert out.count(OLD) == 0
assert out.count(NEW) == 20
open(P, 'wb').write(out)

ob = open('G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc.before_v539.bak', 'rb').read()
diff = [i for i in range(len(out)) if out[i] != ob[i]]
print('size', len(out), 'diff bytes', len(diff))
print('new md5', hashlib.md5(out).hexdigest())