import pickle,struct
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
IDX={}
for i,v in enumerate(CL): IDX.setdefault(v,i)
def slots_for(tag):
    out=[]
    for ch in tag:
        cp=ord(ch)
        if cp not in IDX: return None
        out.append(IDX[cp]+0x20)
    return out
res=pickle.load(open('F:/sr2-cn/_st_ch_recs.pkl','rb'))
blob=open('F:/sr2-cn/_static_blob.bin','rb').read() if False else None
tags=['DISTRICT_SUBURBS','DISTRICT_DOWNTOWN','HOOD_MISTY_LANE','DISTRICT_SUBURBS_EXPANSION','HOOD_DOWNTOWN','HOOD_ROLLERZ_SUBURB']
for t in tags:
    s=slots_for(t)
    print(t,'->',s)
    if not s: continue
    cnt=0
    for off,rs in res:
        n=len(rs)
        for i in range(n-len(s)+1):
            if rs[i:i+len(s)]==s:
                cnt+=1
                print('   HIT %08X len=%d ctx=%s'%(off,n,''.join(chr(CL[x-0x20]) if 0<=x-0x20<len(CL) and x>=0x20 else '^' for x in rs[max(0,i-6):i+len(s)+6])))
    print('   total',cnt)
