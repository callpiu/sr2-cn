import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def U16(s):
    return s.encode('utf-16-be')

blob = v.read(v.find('static_CH', 'le_strings'))
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

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

# 找 QUIT_TO_MAIN_MENU / CONTROL_CANCEL / MENU_TITLE_NOTICE 的中文
TARGETS = {'A935FCF3': '?', '7AB46909': '?', '474361DB': '?', '7898FE46': '?',
           '699F72DA': '?', '922DDF58': '?'}
print('=== 已知 ID -> 中文（用于建立 tag 映射） ===')
for off, o in res:
    h = '%08X' % ((o[0] << 16) | o[1])
    if h in TARGETS:
        print('   %s  %r' % (h, D(o[2:] if len(o) > 2 else o)))

print()
print('=== 英文表里查这些 ID 的原文 ===')
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
b2 = v2.read(v2.find('static_US', 'le_strings'))
res2 = []
i = 0
while i + 2 <= len(b2):
    j = i
    out = []
    while j + 2 <= len(b2):
        x = struct.unpack_from('>H', b2, j)[0]
        if x == 0:
            break
        out.append(x)
        j += 2
        if len(out) > 600:
            break
    if out:
        res2.append((i, out))
        i = j + 2
    else:
        i += 2

def A(sl):
    return ''.join(chr(x) if 32 <= x < 0x7f else '' for x in sl)

for off, o in res2:
    t = A(o[2:] if len(o) > 2 else o)
    if t in ('Quit to Main Menu', 'Cancel', 'Notice', 'Leave Game', 'Single Player',
             'Waiting for Player...', 'Quit', 'OK'):
        print('   ID=%08X  %r' % ((o[0] << 16) | o[1], t))