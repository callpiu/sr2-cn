import pickle
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
res=pickle.load(open('F:/sr2-cn/_st_ch_recs.pkl','rb'))
def T(s):
    return''.join('^%02X'%x if x<0x20 else (chr(CL[x-0x20]) if x-0x20<len(CL) else '?') for x in s)
hits=[]
for off,s in res:
    if len(s)<3: continue
    txt=s[2:]
    t=T(txt).strip()
    if t in ('城','主城','郊区','城郊','市郊','城区','主城区','老城'):
        hits.append((off,len(txt),T(txt)))
print('candidates',len(hits))
for off,l,t in hits: print('%08X  textslots=%d  %r'%(off,l,t))
