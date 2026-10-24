# -*- coding: utf-8 -*-
"""交叉验证：REC2 的 22 个 CJK slot，用各张候选字表解码，看哪张表能得到观测乱码。
观测乱码(用户): 任璨偶巧位... (你->任 的->璨 弟->偶 兄->巧 们->位)
"""
import sys, os, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def load_cl(vp, name):
    buf = vp.read(vp.find(name, 'txt'))
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

# REC1 slots (CJK portion)
rec1_slots = [403, 1868, 1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
rec1_true = '你的弟兄们需要你的保护'

tables = {}
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
tables['patch_CH(2795)'] = load_cl(v, 'charlist_CH')
tables['patch_JP'] = load_cl(v, 'charlist_JP')
tables['JPCharList'] = load_cl(v, 'JPCharList')
pv = Vpp('F:/sr2-cn/pristine/patch.vpp_pc')
tables['official_CH(2838)'] = load_cl(pv, 'charlist_CH')
tables['official_JP'] = load_cl(pv, 'charlist_JP')

# common.vpp_pc 里的 charlist?
try:
    cv = Vpp(os.path.join(G, 'common.vpp_pc'))
    for e in cv.entries():
        n = e['name'].lower()
        if 'charlist' in n or 'font' in n or 'hud' in n:
            print('common.vpp has:', e['name'], e['ext'], e['size'])
except Exception as ex:
    print('common err', ex)

print('\n--- 用各表解码 REC1 的 CJK slots ---')
for name, cl in tables.items():
    out = []
    for s in rec1_slots:
        ci = s - 0x20
        out.append(chr(cl[ci]) if 0 <= ci < len(cl) else '?')
    print('%-20s -> %s' % (name, ''.join(out)))

# 关键：找哪个 (表, 偏移) 组合能把 slot 403 解成 '任'
print('\n--- 寻找能解出观测乱码的表/变换 ---')
target_garble = '任璨偶巧位雄衡伪该'
for name, cl in tables.items():
    for delta in range(-0x40, 0x41):
        out = []
        ok = True
        for s in rec1_slots:
            ci = s + delta - 0x20
            if 0 <= ci < len(cl):
                out.append(chr(cl[ci]))
            else:
                ok = False; break
        if ok:
            s_out = ''.join(out)
            if s_out[0] == '任' or s_out in ('任璨偶巧位雄衡伪该',) or '璨' in s_out:
                print('  %-20s delta=%+d -> %s' % (name, delta, s_out))
