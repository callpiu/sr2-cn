import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

print('=== 找 mod 里用到的、CH 表里确实存在的 tag（用已知中文反查）===')
print('已知：ID 39C7759B = 等待玩家…… (MULTI_COOP_WAITING_PLAYER_2)')
print('      ID 3CAB6F69 = 等待玩家')
print('      ID 12012AE5 = 单人游戏 (Single Player)')
print()

# CH表里"离开游戏"的所有记录ID
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

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

print('CH 表里短 label（1-6 slot）的候选ID：')
for off, o in res:
    t = D(o[2:] if len(o) > 2 else o)
    if t in ('单人游戏', '离开游戏', '等待玩家', '联机游戏', '多人游戏', '合作游戏',
             '排行榜', '继续', '确定', '返回', '取消', '是', '否'):
        print('   %-8s ID=%08X  %r' % ('%08X' % off, (o[0] << 16) | o[1], t))

print()
print('=== 反查：mod 用了 SUI_LAN_COOP_SP 当 body，LEADERBOARDS_SP 当 option_2 ===')
print('=> body 想表达「单人游戏/SP」，option_2 也想表达类似')
print('=> 正确修法：body 和 option_2 换成 CH 表里真实存在的 tag')
print()
print('=== 检查 CH 表里是否有 MULTI_MODE_5 对应的短串 ===')
# MULTI_MODE_5 之前用于 mission skip prompt的 body 组装
for off, o in res:
    t = D(o[2:] if len(o) > 2 else o)
    if '模式' in t and len(t) <= 10:
        print('   %08X ID=%08X %r' % (off, (o[0] << 16) | o[1], t))