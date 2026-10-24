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
print('total',len(res))
hit=[]
for off,slots in res:
    t=dec(slots)
    core=re.sub(r'\^\w\w','',t)
    core=re.sub(r'\[[^\]]*\]','',core)
    core=core.replace('\n','').strip()
    if core=='城区' or core=='城' or core=='郊区' or core=='市郊区' or core=='城郊':
        hit.append((off,len(slots),t))
print('bare hits',len(hit))
for h in hit: print('%08X'%h[0],h[1],repr(h[2]))
