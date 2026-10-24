# -*- coding: utf-8 -*-
"""
v544：修加载画面提示乱码 —— 把 city_load.vint_doc 里loading_text 的字体样式
从 header_n_overlay（拉丁标题字体）改成 bodyital_overlay（中文可渲染，16 字节等长）。
★ 严格等长替换：16 -> 16 字节，VPP 结构与所有偏移完全不变。
"""
import struct, hashlib, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/common.vpp_pc'
BASE = 'f041934f15f06c6facc97d00e1ab7efd'

buf = bytearray(open(P, 'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest() == BASE, 'baseline mismatch'
orig = bytes(buf)
orig_len = len(buf)

v = Vpp(P)
ds = v.data_start if hasattr(v, 'data_start') else 0x9000
e = v.find('city_load', 'vint_doc')
abs_at = ds + e['body']
blob = bytes(buf[abs_at:abs_at + e['size']])
print('city_load.vint_doc: body=%X size=%d abs=%08X' % (e['body'], e['size'], abs_at))

OLD = b'header_n_overlay'   # 16
NEW = b'bodyital_overlay'   # 16
assert len(OLD) == len(NEW), 'must be equal length'

assert blob.count(OLD) == 1, blob.count(OLD)
i = blob.find(OLD)
print('替换位置（vint 内偏移）: %d (0x%X)' % (i, i))

# 上下文确认：必须是 loading_text 的属性
ctx = blob[max(0, i - 60):i + 40]
print('上下文: %r' % ctx)
assert b'loading_text' in ctx and b'text' in ctx, 'context mismatch'

# 执行
newblob = blob[:i] + NEW + blob[i + len(OLD):]
assert len(newblob) == len(blob)
buf[abs_at:abs_at + e['size']] = newblob

out = bytes(buf)
print()
print('== 校验 ==')
# 1) 长度不变
assert len(out) == orig_len, 'file size changed!'
print('  文件长度不变: %d' % len(out))
# 2) 只改了少量字节（两串后8 字节 "overlay" 相同，故差异 < 16）
diff = [k for k in range(len(out)) if out[k] != orig[k]]
print('  差异字节数: %d（%s）' % (len(diff), [hex(x) for x in diff[:8]]))
assert 0 < len(diff) <= 16, len(diff)
assert abs_at + i in diff, '改动位置不在预期处'
# 3) 所有其它 entry 完全未变
chg = []
for x in v.entries():
    a = ds + x['body']
    b = a + x['size']
    if out[a:b] != orig[a:b]:
        chg.append(x['name'] + '.' + x['ext'])
print('  被修改的 entry:', chg)
assert chg == ['city_load.vint_doc'], chg

open(P, 'wb').write(out)
print()
print('new md5', hashlib.md5(out).hexdigest())

# 回读验证
v2 = Vpp(P)
d2 = v2.read(v2.find('city_load', 'vint_doc'))
print()
print('== 回读 ==')
print('  header_n_overlay 残留:', d2.count(b'header_n_overlay'))
print('  bodyital_overlay 存在:', d2.count(b'bodyital_overlay'))
print('  loading_text 仍在:', d2.count(b'loading_text'))
i2 = d2.find(b'bodyital_overlay')
print('  上下文: %r' % d2[max(0, i2 - 60):i2 + 40])