import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
M = cl(os.path.join(G,"patch.vpp_pc"))

def try_decode(raw, T):
    """按 (tag<<8|val) 规则解码, 返回 (可读汉字数, 越界码数, 样例)"""
    cjk=0; bad=0; asc=0; sample=[]
    i=0
    while i+1 < len(raw):
        v=(raw[i]<<8)|raw[i+1]; i+=2
        if v==0: continue
        if v<32: bad+=1; continue
        if v<0x8000:
            k=v-32
            if 0<=k<len(T):
                c=chr(T[k])
                if 0x4E00<=ord(c)<0x9FFF: cjk+=1
                elif 32<=ord(c)<127: asc+=1
                else: bad+=1
                if len(sample)<4000: sample.append(c)
            else: bad+=1
        else:
            bad+=1
    return cjk,bad,asc,"".join(sample)

def files():
    for f in ("common.vpp_pc","patch.vpp_pc"):
        yield "VPP:"+f, os.path.join(G,f)
    for dp,_,fns in os.walk(os.path.join(G,"Mods")):
        for fn in fns:
            if fn.lower().endswith(".le_strings") or 'strings' in fn.lower():
                yield "LOOSE:"+fn, os.path.join(dp,fn)

for tag,p in files():
    try:
        if p.endswith((".vpp_pc",)):
            v=Vpp(p); items=[(e['name']+"."+e.get('ext',''), v.read(e)) for e in v.entries() if 'string' in e.get('ext','')]
        else:
            items=[(os.path.basename(p), open(p,'rb').read())]
    except Exception as ex:
        print("%-40s ERR %s"%(tag,ex)); continue
    for name, b in items:
        n = struct.unpack_from('<I', b, 8)[0]
        if n<=0 or 16+n*8>len(b): 
            continue
        raw = b[16+n*8:]
        cjkM,badM,ascM,sM = try_decode(raw, M)
        cjkO,badO,ascO,sO = try_decode(raw, O)
        totM=cjkM+ascM; totO=cjkO+ascO
        scoreM = cjkM/max(1,totM); scoreO = cjkO/max(1,totO)
        print("%-34s %-22s CJK M=%5d(%.2f) O=%5d(%.2f) 越界 M=%d O=%d" %
              (tag[:34], name[:22], cjkM, scoreM, cjkO, scoreO, badM, badO))
