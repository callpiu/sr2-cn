"""修复两件事：
   1. juice_CH.cxt 缺失的 3 个 key（对应菜单里的空白项）
   2. vf3 里 ASCII 的 width：从 31 调回 18（对齐原厂）

关于 width
    原厂和第三方的 vf3 头部参数完全相同（Width 29 / RenderHeight 28 / CharSpacing -5）
    记录字段只有 ASCII 的 width 差 1（原厂 18，第三方 17）
    第三方 CJK 是 30，与原厂相同 —— 说明 CJK 没问题

    之前我把 ASCII 改成 31 后字母显示出来了，但间距过大
    => 回调到 18（与原厂一致），观察间距

关于 .cxt
    juiced_CH.cxt 是 [KEY] + 正文 + 3 空行 的格式，CRLF 换行
    US 版有 54 个 key，CH 版只有 51 个，缺 J_MOUSEFOV / J_FINEAIMONLY / J_FOVMULT
"""
import sys, os, re, struct

sys.path.insert(0, r'F:\sr2-cn\pylibs')
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

W = r'F:\sr2-cn'
G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
J = os.path.join(G, 'Mods', 'JUICED - Strings')
OUT = os.path.join(W, '_juice_fix', 'out4')
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 修 .cxt ----------
ch_raw = open(os.path.join(J, 'juiced_CH.cxt'), 'rb').read()
us_raw = open(os.path.join(J, 'juiced_US.cxt'), 'rb').read()
print('.cxt 换行检查: CH 以 CRLF 结尾=%s, US 以 CRLF 结尾=%s'
      % (ch_raw.endswith(b'\r\n'), us_raw.endswith(b'\r\n')))
print('.cxt CR 计数: CH=%d US=%d ; LF 计数: CH=%d US=%d'
      % (ch_raw.count(b'\r'), us_raw.count(b'\r'), ch_raw.count(b'\n'), us_raw.count(b'\n')))

ch = ch_raw.decode('utf-8')
us = us_raw.decode('utf-8')


def blocks(s):
    """把 [KEY] ... 切成 dict（保留原始文本片段）"""
    out = {}
    for m in re.finditer(r'\[([A-Za-z0-9_]+)\]\r?\n(.*?)(?=\r?\n\[|\Z)', s, re.S):
        out[m.group(1)] = m.group(2)
    return out


bc, bu = blocks(ch), blocks(us)
missing = [k for k in bu if k not in bc]
print()
print('CH 缺少的 key: %s' % missing)
for k in missing:
    v = ' '.join(bu[k].split())
    print('  [%s] = %r' % (k, v))

if missing:
    add = ''
    for k in missing:
        add += '\r\n[%s]\r\n%s\r\n\r\n' % (k, bu[k].strip('\r\n'))
    # 插到最后一个 key 之前（保持 MP_SERVER_IP 在末尾）
    idx = ch.find('\r\n[MP_SERVER_IP]')
    if idx < 0:
        new_ch = ch.rstrip('\r\n') + '\r\n' + add
    else:
        new_ch = ch[:idx] + '\r\n' + add.lstrip('\r\n') + ch[idx:].lstrip('\r\n')
    # 写盘前把裸 \n 统一成 CRLF
    new_ch = new_ch.replace('\r\n', '\n').replace('\n', '\r\n')
    # 保证文件末尾特征与源文件一致
    src_ends = ch_raw.endswith(b'\r\n')
    if src_ends and not new_ch.endswith('\r\n'):
        new_ch += '\r\n'
    if not src_ends and new_ch.endswith('\r\n'):
        new_ch = new_ch.rstrip('\r\n')
    nb = new_ch.encode('utf-8')
    print()
    print('新 .cxt: %d -> %d 字节; CRLF 结尾=%s; CR=%d LF=%d'
          % (len(ch_raw), len(nb), nb.endswith(b'\r\n'), nb.count(b'\r'), nb.count(b'\n')))
    open(os.path.join(OUT, 'juiced_CH.cxt'), 'wb').write(nb)
    print('写出 %s' % os.path.join(OUT, 'juiced_CH.cxt'))

# ---------- 2. 修 vf3 的 ASCII width ----------
SRC = os.path.join(W, '_juice_fix', 'patch.vpp_pc')
v = Vpp(SRC)
vf3 = bytearray(v.read(v.find('fnt_chinese', 'vf3_pc')))
N = struct.unpack_from('<i', vf3, 0x08)[0]
CH0 = 0xD0
NEW = 18
n = 0
for i in range(95):
    off = CH0 + i * 16
    if struct.unpack_from('<h', vf3, off)[0] != NEW:
        struct.pack_into('<h', vf3, off, NEW)
        struct.pack_into('<h', vf3, off + 12, NEW)
        n += 1
print()
print('ASCII width -> %d : %d 个' % (NEW, n))
assert len(vf3) == 67268
v2 = Vpp(SRC)
v2.replace_body_appended(v2.find('fnt_chinese', 'vf3_pc'), bytes(vf3))
v2.save(os.path.join(OUT, 'patch.vpp_pc'))
print('写出 %s (%d 字节)' % (os.path.join(OUT, 'patch.vpp_pc'),
                            os.path.getsize(os.path.join(OUT, 'patch.vpp_pc'))))
