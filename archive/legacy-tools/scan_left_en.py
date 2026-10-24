# -*- coding: utf-8 -*-
"""扫描剩余纯英文残留（排除电台/枪名/涂装/格式串），找出真正的店名与地名"""
import struct, sys, re, json
sys.path.insert(0, 'F:/sr2.cn/x') if False else None
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f:
            out.append(chr(x))
        else:
            return None
    return ''.join(out)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

# 已知不翻的（电台台标 / 枪械型号 / 涂装代号 / 技术串）
SKIP = re.compile(
    r'Volition|Skeeters|KRHYME|GDHC|Funk 98|K12 |RFS 87|KBOOM|Sizzurp|Ghettoblaster|'
    r'Four 20|Shepherd|89 GEN|Ezzzy|Doo Rag|Rhombus|6 Loops|^\d+\.?\d*\s|'
    r'Ultimax|XMAC|SAW|AR-?50|AR200|AR-40|AS12|AS14|XS-2|SKR-|CKH|T3K|SR Air|'
    r'12 Gauge|Kobra|Zebra|Razor|Titan|Enforcer|Dominator|Bandit|Regulator|'
    r'Ghost|Splatster|Hammerhead|Panther|Reaper|Rattlesnake|Shark|Swallow|Swan|'
    r'Ruckus|Sunsinger|Gaslamp|Prephop|Ezpata|Gigatruck|NR4|RFG|Phoenix|K6 Krukov|'
    r'Skin0\d|CUST_VARIANT|TrueSkill|XBOX LIVE|Xbox LIVE|GameStop|'
    r'FRECKLE|Freckle|Romero|Sum Old|Sum Yung|Roje|Sanchez|Dookie|Donovan|'
    r'Double-Stuff|Duck Trucks|Donkey|Feed Dogs|Gyro |Ratty|'
    r'^\*\{|^\{|^%|^XX|^x$|^\*/$|^HOS|^/|^\[|^abc|^PCP$|^SUV$|^GAL|^RJ$|^OG$|'
    r'^ODD$|^AI$|^HUD$|^J$|^U$|^T-Rex$|^Tee|^Lik-a-Chik|^Hi-Fidelity|'
    r'^\[format|^\[color|^\[image|^\[scale|^Skin|^CUST')

rows = []
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ').strip()
    core = re.sub(r'[\x02-\x1f]', ' ', core).strip()
    if not core or not core.isascii():
        continue
    if SKIP.search(core):
        continue
    if len(core) < 3:
        continue
    rows.append((off, (o[0] << 16) | o[1], core, len(o) - 2))

print('剩余可疑英文条目:', len(rows))
print()
for off, h, core, ln in rows:
    print('  off=%08X ID=%08X slots=%-3d %r' % (off, h, ln, core[:80]))

json.dump([[a, b, c, d] for a, b, c, d in rows],
          open('F:/sr2-cn/_left_en.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)