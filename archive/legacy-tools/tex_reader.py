import sys, struct, re
import numpy as np
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

TEX="G:/SteamLibrary/steamapps/common/Saints Row 2/textures.vpp_pc"

def open_vpp_header(path):
    with open(path,'rb') as f:
        d=f.read(5+0x14F+20)
    assert d[:5]==S.MAGIC_VPP
    o=5+0x14F
    num,container_size,len_offsets,len_filenames,len_extensions=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+len_offsets)&0xFFFFF800)+0x800
    ext_at=((names_at+len_filenames)&0xFFFFF800)+0x800
    data_start=((ext_at+len_extensions)&0xFFFFF800)+0x800
    return dict(num=num,data_start=data_start,names_at=names_at,ext_at=ext_at,
                len_offsets=len_offsets,len_filenames=len_filenames,len_extensions=len_extensions)

H=open_vpp_header(TEX)
print("textures header:",H)

# read entry table + names region
with open(TEX,'rb') as f:
    f.seek(0x800)
    etab=f.read(H['num']*28)
    f.seek(H['names_at'])
    names=f.read(H['len_filenames']+200)
    f.seek(H['ext_at'])
    exts=f.read(H['len_extensions']+200)

def getstr(base,off):
    e=base.find(b'\x00',off)
    return base[off:e].decode('ascii','replace')

entries=[]
for i in range(H['num']):
    a,b,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
    name=getstr(names,a); ext=getstr(exts,b) if b else ''
    entries.append((name,ext,d,ln))

print("\nentries matching chinese|fnt|peg:")
for name,ext,d,ln in entries:
    n=name+("."+ext if ext else '')
    if re.search(r'chinese|fnt|peg|atlas',n,re.I):
        print(f"  {n:40s} body={d} size={ln}")
