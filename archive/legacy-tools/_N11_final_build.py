# -*- coding: utf-8 -*-
"""生成最终修复版 charlist_CH.txt：
  - 官方原版注释头（逐字节取自 vpp_backup/patch.vpp_pc.orig）
  - count=2795（与当前补丁数据体的项数一致）
  - CRLF 行尾
  - 结尾 //ENDOFFILE
"""
import sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('charlist_CH', 'txt'))
toks = [int(x) for x in raw.split() if x.lstrip(b'-').isdigit()]
N = len(toks)

vo = Vpp(r'F:\sr2-cn\vpp_backup\patch.vpp_pc.orig')
ro = vo.read(vo.find('charlist_CH', 'txt'))
hdr = ro[:ro.find(b'count=')]                 # 官方注释头（含 CRLF）

out = bytearray(hdr)
out += b'count=%d\r\n' % N
out += b'\r\n'.join(str(t).encode() for t in toks)
out += b'\r\n//ENDOFFILE\r\n'

open('F:/sr2-cn/_fixed_charlist_CH.txt', 'wb').write(bytes(out))
print("生成 _fixed_charlist_CH.txt: %d 字节 (原补丁 %d)" % (len(out), len(raw)))
print("  头部:", repr(bytes(out[:80])))
print("  count 行:", repr(bytes(out[hdr.__len__():hdr.__len__() + 16])))
print("  尾部:", repr(bytes(out[-30:])))
print("  CRLF 数:", bytes(out).count(b'\r\n'), " 单独 LF:", bytes(out).count(b'\n') - bytes(out).count(b'\r\n'))

# 解析自检
m = re.search(rb'count=(\d+)\r\n', bytes(out))
print("  解析 count =", m.group(1).decode(), " 期望 =", N)
body = bytes(out)[m.end():]
end = body.find(b'//ENDOFFILE')
body = body[:end] if end >= 0 else body
parsed = [int(x) for x in re.findall(rb'\d+', body)]
print("  解析项数 =", len(parsed), " 期望 =", N)
print("  一致:", len(parsed) == N)
