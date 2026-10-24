# -*- coding: utf-8 -*-
"""生成修复版 charlist_CH.txt
- 使用官方原版的注释头（逐字节取自 vpp_backup/patch.vpp_pc.orig）
- 但 count= 与数据体用【当前补丁的 2795 项】（因为 static/voice_script 的 slot 是按它编的）
"""
import sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

# 当前补丁的字符数据
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('charlist_CH', 'txt'))
toks = [int(x) for x in raw.split() if x.lstrip(b'-').isdigit()]
N = len(toks)
print("当前补丁项数 =", N)

# 官方原版的注释头（取到 count= 之前）
vo = Vpp(r'F:\sr2-cn\vpp_backup\patch.vpp_pc.orig')
ro = vo.read(vo.find('charlist_CH', 'txt'))
i = ro.find(b'count=')
official_hdr = ro[:i]                              # 注释头（含换行）
print("官方注释头 =", repr(official_hdr))

hdr = official_hdr + b'count=%d\r\n' % N
body = b'\r\n'.join(str(t).encode() for t in toks) + b'\r\n'
out = hdr + body

open('F:/sr2-cn/_fixed_charlist_CH.txt', 'wb').write(out)
print("\n已生成 _fixed_charlist_CH.txt: %d 字节" % len(out))
print(repr(out[:300]))
print("...")
print(repr(out[-50:]))

# 校验
hdr_ok = out.startswith(b'//Used character list')
cnt = re.search(rb'count=(\d+)', out).group(1)
print("\n头部OK:", hdr_ok, " count =", cnt.decode())
t2 = [int(x) for x in out.split() if x.lstrip(b'-').isdigit()]
print("数字 token 数 =", len(t2), "(= N+1 =", N + 1, ")")
print("反斜杠正常:", b"'d:\\projects" in out)
