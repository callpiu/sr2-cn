# -*- coding: utf-8 -*-
"""检验：static_CH 里是否存在与活动串【同文】的其他记录（同文双记录陷阱，v415 教训）

铁律：搜索必须先在正样本上自检 —— 先确认能搜到已知的 REC1/REC2，再谈"搜不到"。
"""
import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")

def load_charlist(vp,name="charlist_CH"):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp)

def texts_of(lesname):
    e=vp.find(lesname,"le_strings")
    if not e: return [],None
    data=vp.read(e)
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    assert magic==0xA84C7F73, (lesname,hex(magic))
    off=12+buckets*8
    ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
    out=[]
    for o in ptrs:
        if o+4>len(data): continue
        id1,id2=struct.unpack_from('<HH',data,o)
        p=o+4; ch=[]
        while p+1<len(data):
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            p+=2; ci=s-0x20
            ch.append(chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD')
        out.append((((id1<<16)|id2), "".join(ch)))
    return out,(buckets,count)

TARGETS={0x84F287ED:"REC1", 0x10AF1E62:"REC2"}

for les in ["static_CH","voice_script_CH","platform_pc_CH"]:
    recs,info=texts_of(les)
    if recs is None: continue
    print(f"\n===== {les}  buckets={info[0]} count={info[1]} records={len(recs)} =====")
    # ---- 正样本自检 ----
    hits={h:t for h,t in recs if h in TARGETS}
    for h,lab in TARGETS.items():
        if h in hits: print(f"  [自检] {lab} {h:#010x} 找到: {hits[h]!r}")
        else:         print(f"  [自检] {lab} {h:#010x} 未找到")
    # ---- 同文搜索：含关键片段的所有记录 ----
    keys=["弟兄","袭击","谈几笔生意","免遭","需要你的保护","生意"]
    for k in keys:
        m=[(h,t) for h,t in recs if k in t]
        print(f"  含「{k}」: {len(m)} 条")
        for h,t in m[:12]:
            tag = TARGETS.get(h,"")
            print(f"     {h:#010x}{('★'+tag) if tag else ''}  {t[:70]}")
