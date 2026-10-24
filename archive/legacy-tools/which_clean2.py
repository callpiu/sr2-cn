# -*- coding: utf-8 -*-
"""解码所有 patch 备份里的 REC1/REC2，找出哪份是【未被实验污染】的干净原文"""
import sys, struct, re, os, hashlib, glob
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
TARGETS={0x84F287ED:"REC1", 0x10AF1E62:"REC2"}

cands = sorted(glob.glob(game+"patch.vpp_pc*")) + [r"F:/sr2-cn/_v534_build.vpp_pc"]
for path in cands:
    name=os.path.basename(path)
    try:
        vp=S.Vpp(path)
        e=vp.find("charlist_CH","txt")
        if not e: print(f"{name:52s} (无 charlist_CH, skip)"); continue
        buf=vp.read(e); end=buf.find(b'//ENDOFFILE')
        cl=[int(x) for x in re.findall(rb'\d+', buf[:end if end>0 else len(buf)])]
        ent=vp.find("static_CH","le_strings")
        if not ent: print(f"{name:52s} (无 static_CH)"); continue
        data=vp.read(ent)
        magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
        off=12+buckets*8
        ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
        found={}
        for o in ptrs:
            if o+4>len(data): continue
            id1,id2=struct.unpack_from('<HH',data,o)
            h=(id1<<16)|id2
            if h in TARGETS:
                p=o+4; ch=[]
                while p+1<len(data):
                    s=struct.unpack_from('>H',data,p)[0]
                    if s==0: break
                    p+=2; ci=s-0x20
                    ch.append(chr(cl[ci]) if 0<=ci<len(cl) else '?')
                found[h]="".join(ch)
        m=hashlib.md5(open(path,'rb').read()).hexdigest()[:10]
        line=f"{name:52s} {m} bk={buckets:<5d}"
        for h,lab in TARGETS.items():
            t=found.get(h)
            if t is None: line+=f" | {lab}=<无>"
            else:
                # 压缩尾部空格便于阅读
                disp=t.rstrip()
                nsp=len(t)-len(disp)
                line+=f"\n      {lab}={disp!r}" + (f"  (+{nsp}空格)" if nsp else "")
        print(line)
        del vp
    except Exception as ex:
        print(f"{name:52s} ERROR {ex}")
