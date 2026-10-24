import pickle,re
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
def dec(slots):
    out=[]
    for s in slots:
        if s==0: break
        if s<0x20: out.append('^%02X'%s); continue
        i=s-0x20
        out.append(chr(CL[i]) if 0<=i<len(CL) else '?')
    return ''.join(out)
res=pickle.load(open('F:/sr2-cn/_st_ch_recs.pkl','rb'))
seen={}
for off,slots in res:
    t=dec(slots)
    core=re.sub(r'\[[^\]]*\]','',t)
    core=re.sub(r'\^\w\w','',core)
    for m in re.finditer('城区',core):
        a=max(0,m.start()-3); b=min(len(core),m.end()+3)
        ctx=core[a:b]
        seen.setdefault(ctx,[]).append('%08X:%d'%(off,len(slots)))
for k,v in sorted(seen.items(), key=lambda x:-len(x[1])):
    print(len(v), repr(k), v[:3])
