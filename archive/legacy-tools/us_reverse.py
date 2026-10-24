# -*- coding: utf-8 -*-
"""从英文表 static_US 反查：活动提示的英文原文到底对应哪些 hash，
再看中文表同 hash 的翻译 —— 找出用户看到的到底是那一条。"""
import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")

def dec(lesname, cl=None):
    e=vp.find(lesname,"le_strings")
    if not e: return {}
    data=vp.read(e)
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    assert magic==0xA84C7F73
    off=12+buckets*8
    ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
    out={}
    for o in ptrs:
        if o+4>len(data): continue
        id1,id2=struct.unpack_from('<HH',data,o)
        p=o+4; ch=[]
        while p+1<len(data):
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            p+=2
            if cl is None:                 # 英文：slot 即 ASCII/Latin1
                ch.append(chr(s) if 32<=s<127 else ('\uFFFD' if s else ''))
            else:
                ci=s-0x20
                ch.append(chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD')
        out[(id1<<16)|id2]="".join(ch)
    return out

e=vp.find("charlist_CH","txt"); buf=vp.read(e)
end=buf.find(b'//ENDOFFILE')
cl=[int(x) for x in re.findall(rb'\d+', buf[:end if end>0 else len(buf)])]

US=dec("static_US")
CH=dec("static_CH", cl)
print(f"static_US={len(US)}  static_CH={len(CH)}")

keys=["homie","protect","protect them","heading out","deal","attack"]
seen=set()
for h,t in US.items():
    tl=t.lower()
    if any(k in tl for k in keys):
        if h in seen: continue
        seen.add(h)
        cn=CH.get(h)
        if cn is None: continue
        n_cjk=sum(1 for c in cn if ord(c)>0x2000)
        mark=""
        if h in (0x84F287ED,0x10AF1E62): mark=" ★已知REC"
        if n_cjk in (11,22): mark+=" ★字数吻合"
        print(f"\n{h:#010x}{mark}\n   EN: {t[:110]}\n   CN: {cn.rstrip()[:110]}   [CJK={n_cjk}]")
