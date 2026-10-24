# -*- coding: utf-8 -*-
"""对比 common vf3 与 patch vf3 的头部结构, 确认可互换"""
import sys, struct
sys.path.insert(0,'.')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

def dump_vf3(p, name='fnt_chinese', ext='vf3_pc'):
    v=Vpp(p); e=v.find(name,ext); b=v.data_start+e['body']
    raw=v.data[b:b+e['size']]
    print(f'--- {p.split("/")[-1]} {name}.{ext} size={e["size"]} ---')
    print('  head 0x00:',raw[:16].hex(' '))
    print('  magic:',raw[:4], 'ver:',struct.unpack_from('<I',raw,4)[0], 'N:',struct.unpack_from('<I',raw,8)[0])
    print('  u32[16:40]:',[hex(x) for x in struct.unpack_from('<6I',raw,16)])
    print('  0xB0..0xE0:',raw[0xB0:0xE0].hex(' '))
    # 验证记录区起点
    for hdr in (0xBC,0xD0):
        N=struct.unpack_from('<I',raw,8)[0]
        u_off=hdr+N*16; v_off=u_off+N*4; end=v_off+N*4
        print(f'  hdr={hdr:#x}: recEnd={hdr+N*16:#x} uOff={u_off:#x} vOff={v_off:#x} end={end:#x} (size={len(raw):#x}) {"MATCH" if end==len(raw) else "NO"}')
    return raw

r1=dump_vf3(G+'/common.vpp_pc')
print()
r2=dump_vf3(G+'/patch.vpp_pc')
print()
# 图集
def dump_peg(p):
    v=Vpp(p); e=v.find('fnt_chinese','g_peg_pc'); b=v.data_start+e['body']
    raw=v.data[b:b+e['size']]
    print(f'{p.split("/")[-1]} fnt_chinese.g_peg_pc size={e["size"]} head:',raw[:48].hex(' '))
    return raw
dump_peg(G+'/patch.vpp_pc')
v=Vpp(G+'/textures.vpp_pc'); e=v.find('fnt_chinese',''); b=v.data_start+e['body']
raw=v.data[b:b+e['size']]
print(f'textures.vpp_pc fnt_chinese size={e["size"]} head:',raw[:48].hex(' '))
