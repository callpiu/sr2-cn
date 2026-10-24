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
for kw in ['迷雾巷','教堂滩','圣徒街区','工业区','港口','工业区','拓展区','扩展区']:
    h=[(off,len(s),dec(s)) for off,s in res if kw in dec(s)]
    print(kw, len(h))
    for x in h[:6]: print('   %08X %d %s'%(x[0],x[1],x[2][:80]))
