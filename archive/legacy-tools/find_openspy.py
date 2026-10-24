# -*- coding: utf-8 -*-
"""在 platform_pc_CH 里精确定位 OpenSpy 登录界面相关记录"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    out = []
    for x in sl:
        if x < 0x20: out.append(chr(x))
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f: out.append(chr(x))
        else: return None
    return ''.join(out)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
R = scan(v.read(v.find('platform_pc_CH', 'le_strings')))
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
US = scan(v2.read(v2.find('platform_pc_US', 'le_strings')))
us = {}
for off, o in US:
    if len(o) > 2:
        t = A(o[2:])
        if t: us.setdefault((o[0] << 16) | o[1], t.strip())

# 截图上出现的界面文本
KEY = ['登录', '登出', '登录失败', '登录错误', '未登录', '创建账号', '在线',
       '邮箱', '密码', '昵称', '进入', '退出']
print('%-9s %-9s %-4s %-22s %s' % ('off', 'ID', 'slot', '中文', '英文'))
print('-' * 95)
for off, o in R:
    if len(o) < 3: continue
    t = D(o[2:]).strip()
    h = (o[0] << 16) | o[1]
    en = us.get(h, '')
    # 中文含关键词，或英文含Sign/Log In/Out
    if any(k in t for k in KEY) or re.search(r'Sign|Log ?In|Log ?Out|Email|Nickname|Enter Password', en, re.I):
        print('%-9X %08X %-4d %-22r %r' % (off, h, len(o) - 2, t, en))