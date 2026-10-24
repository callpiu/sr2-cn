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

TAGS = ['MULTI_COOP_WAITING_PLAYER_2', 'SUI_LAN_COOP_SP', 'LEADERBOARDS_SP',
        'OPTION_YES', 'OPTION_NO', 'MULTI_MODE_5', 'MISSION_COOP_SKIP_PROMPT']

def S(c):
    return struct.pack('>H', CL.index(ord(c)) + 0x20)

def U16(s):
    return s.encode('utf-16-be')

for nm in ['static_CH', 'voice_script_CH', 'platform_pc_CH']:
    blob = v.read(v.find(nm, 'le_strings'))
    print('===', nm)
    for t in TAGS:
        # le_strings 里ASCII 也是 slot 编码，等价 UTF-16BE
        print('   %-30s %d' % (t, blob.count(U16(t))))

print()
print('=== 英文 static_US ===')
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
b2 = v2.read(v2.find('static_US', 'le_strings'))
for t in TAGS:
    i = b2.find(U16(t))
    if i >= 0:
        j = i + len(t) * 2
        out = []
        while j + 2 <= len(b2):
            x = struct.unpack_from('>H', b2, j)[0]
            if x == 0:
                break
            out.append(chr(x) if 32 <= x < 0x7f else '?')
            j += 2
        print('   %-30s FOUND %r' % (t, ''.join(out)))
    else:
        print('   %-30s not in US' % t)