import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

# 中文表里"等待玩家……"的记录ID，与英文表对应ID比对
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
blob = v.read(v.find('static_CH', 'le_strings'))

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def dec(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

res = []
i = 0
while i + 2 <= len(blob):
    j = i
    out = []
    while j + 2 <= len(blob):
        x = struct.unpack_from('>H', blob, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 600:
            break
    if out:
        res.append((i, out))
        i = j + 2
    else:
        i += 2

# 收集所有极短记录（1-4 个中文 slot）—— 界面 label 多为短串
print('=== 短记录（文本 <=4 slot）样本 ===')
short = [(off, o) for off, o in res if 3 <= len(o) <= 6]
print('count', len(short))
for off, o in short[:40]:
    print('%08X  ID=%08X  %s' % (off, (o[0] << 16) | o[1], dec(o[2:])))
print()
# 目标几条的 ID
for off, o in res:
    t = dec(o[2:] if len(o) > 2 else o)
    if t in ('等待玩家……', '离开游戏', '单人游戏', '等待玩家'):
        print('%-08X ID=%08X slots=%d  %r' % (off, (o[0] << 16) | o[1], len(o), t))