import struct, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

TAG = 'SUI_LAN_COOP_SP'

print('=== 1) 各语言表里搜这个 tag（多编码） ===')
v = Vpp('G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc')
for e in v.entries():
    nm = e['name'] + '.' + e['ext']
    if 'le_strings' not in nm:
        continue
    if not any(k in nm for k in ['platform', 'static', 'voice']):
        continue
    blob = v.read(e)
    c1 = blob.count(TAG.encode('utf-16-be'))
    c2 = blob.count(TAG.encode('utf-16-le'))
    c3 = blob.count(TAG.encode())
    if c1 or c2 or c3:
        print('  %-32s be=%d le=%d raw=%d' % (nm, c1, c2, c3))

print()
print('=== 2) patch 内所有文本类条目 ===')
for e in v.entries():
    nm = e['name'] + '.' + e['ext']
    blob = v.read(e)
    if blob.count(TAG.encode()) or blob.count(TAG.encode('utf-16-be')) or blob.count(TAG.encode('utf-16-le')):
        print('  HIT', nm, e['size'], 'raw', blob.count(TAG.encode()),
              'be', blob.count(TAG.encode('utf-16-be')),
              'le', blob.count(TAG.encode('utf-16-le')))

print()
print('=== 3) 短前缀 SUI_LAN 在 patch 任意编码 ===')
for probe in ['SUI_LAN', 'SUI_', 'LAN_COOP']:
    rb = probe.encode()
    be = probe.encode('utf-16-be')
    le = probe.encode('utf-16-le')
    print('  %-10s raw=%d be=%d le=%d' % (probe, blob.count(rb), blob.count(be), blob.count(le)))

print()
print('=== 4) 官方原版 patch 里搜 ===')
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
for e in v2.entries():
    nm = e['name'] + '.' + e['ext']
    blob = v2.read(e)
    n = blob.count(TAG.encode('utf-16-be')) + blob.count(TAG.encode('utf-16-le')) + blob.count(TAG.encode())
    if n:
        print('  HIT', nm, e['size'], n)