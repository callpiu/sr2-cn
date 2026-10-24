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
    core=re.sub(r'\^\w\w','',core).strip()
    if '城' in core and len(core)<=8:
        seen.setdefault(core,[]).append('%08X(%d)'%(off,len(slots)))
for k,v in sorted(seen.items()):
    print(repr(k), len(v), v[:4])
