import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def hdrstrings(vpp,name,ext,tag):
    v=Vpp(vpp); b=v.read(v.find(name,ext)); N=struct.unpack_from('<I',b,8)[0]
    print("=== %s  N=%d len=%d ==="%(tag,N,len(b)))
    # 头部 0xBC 内的所有可打印串
    i=0; found=[]
    while i < 0xBC:
        j=i
        while j < 0xBC and 32 <= b[j] < 127: j+=1
        if j-i >= 3: found.append((hex(i), b[i:j].decode('ascii','replace')))
        i = j+1
    for off,s in found: print("   @%-6s '%s'" % (off,s))
    print("   头部其它字 @0x0C w=%d @0x10 h=%d @0x14=0x%X @0x18=0x%X @0x1C=0x%X @0x20=0x%X @0x24=%d"%(
        struct.unpack_from('<I',b,0xC)[0], struct.unpack_from('<I',b,0x10)[0],
        struct.unpack_from('<I',b,0x14)[0], struct.unpack_from('<I',b,0x18)[0],
        struct.unpack_from('<I',b,0x1C)[0], struct.unpack_from('<I',b,0x20)[0],
        struct.unpack_from('<I',b,0x24)[0]))
    return b
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
hdrstrings(os.path.join(G,"common.vpp_pc"),"fnt_chinese","vf3_pc","我的 vf3 (common)")
hdrstrings(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","vf3_pc","官方 vf3 (patch.orig)")
# 搜 nobdr
print("\n=== 搜索 fnt_chinese 相关条目 (所有VPP) ===")
for f in ("common.vpp_pc","patch.vpp_pc","textures.vpp_pc"):
    p=os.path.join(G,f)
    try: v=Vpp(p)
    except Exception as e: print(f,"ERR",e); continue
    for e in v.entries():
        if 'chinese' in e['name'].lower() or 'nobdr' in e['name'].lower():
            print("   %-16s %-30s .%-10s size=%d"%(f,e['name'],e.get('ext',''),e['size']))
