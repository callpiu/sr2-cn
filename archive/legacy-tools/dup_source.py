# -*- coding: utf-8 -*-
"""查第二数据源：1) patch.vpp_pc 内是否有多个 static_CH 条目
2) 其他 VPP 里是否含 static_CH / 活动 hash  3) 松散文件覆盖"""
import sys, struct, os, glob
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"

print("=== 1) patch.vpp_pc 内所有 static_* / platform / voice 条目 ===")
vp=S.Vpp(game+"patch.vpp_pc")
for e in vp.entries():
    n=e['name']+('.'+e['ext'] if e['ext'] else '')
    if n.startswith(('static','voice_script','platform')):
        print(f"   {n:28s} body={e['body']:<12d} size={e['size']}")
print("   patch.vpp_pc 总条目:", vp.num)

print("\n=== 2) 其他 VPP 里是否有 static_CH / voice / platform 条目 ===")
import re
def hdr(path):
    with open(path,'rb') as f: d=f.read(5+0x14F+20)
    assert d[:5]==S.MAGIC_VPP, path
    o=5+0x14F
    num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800
    ext_at=((names_at+lf)&0xFFFFF800)+0x800
    ds=((ext_at+le)&0xFFFFF800)+0x800
    return num,ds,names_at,ext_at,lo,lf,le
for vpname in ["common.vpp_pc","chunks1.vpp_pc","chunks2.vpp_pc","chunks3.vpp_pc","chunks4.vpp_pc",
               "anims.vpp_pc","audio.vpp_pc","city_load.vpp_pc","cutscenes.vpp_pc","hmaps.vpp_pc",
               "meshes.vpp_pc","pegs.vpp_pc","music1.vpp_pc","music2.vpp_pc","music3.vpp_pc","music4.vpp_pc"]:
    p=game+vpname
    if not os.path.exists(p): continue
    try:
        num,ds,na,ea,lo,lf,le=hdr(p)
        with open(p,'rb') as f:
            f.seek(0x800); etab=f.read(num*28)
            f.seek(na); names=f.read(lf+400)
            f.seek(ea); exts=f.read(le+400)
        def gs(b,o):
            e2=b.find(b'\x00',o); return b[o:e2].decode('ascii','replace')
        found=[]
        for i in range(num):
            a,b2,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
            nm=gs(names,a); ex=gs(exts,b2) if b2 else ''
            if re.match(r'(static|voice_script|platform)',nm,re.I):
                found.append((nm+('.'+ex if ex else ''), ln))
        if found:
            print(f"   {vpname}: {found}")
    except Exception as ex:
        print(f"   {vpname}: ERR {ex}")
print("   （无输出=这些 VPP 里没有字符串表）")

print("\n=== 3) 松散文件：游戏目录内所有 static_*.le_strings / *.vpp_pc (非根目录) ===")
for dirpath,dirs,files in os.walk(game):
    for fn in files:
        if fn.lower().startswith('static_') and fn.lower().endswith('.le_strings'):
            p=os.path.join(dirpath,fn)
            print(f"   {os.path.relpath(p,game)}  {os.path.getsize(p)}")
        if fn.lower().endswith('.vpp_pc') and os.path.abspath(dirpath)!=os.path.abspath(game):
            print(f"   [VPP] {os.path.relpath(os.path.join(dirpath,fn),game)}  {os.path.getsize(os.path.join(dirpath,fn))}")
