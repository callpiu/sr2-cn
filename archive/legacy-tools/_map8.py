import pickle,struct
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
res=pickle.load(open('F:/sr2-cn/_st_ch_recs.pkl','rb'))
d=dict((off,s) for off,s in res)
for off in [0x6AB3C,0x1EFC6,0x35376,0x57020,0x61694,0x43C5E]:
    s=d.get(off)
    if s is None: print('%08X not found'%off); continue
    print('%08X'%off, ['%04X'%x for x in s])
    # 假设前2个是 ID (LE)
    if len(s)>=3:
        id1=s[0]&0xFF; id2=s[0]>>8
        h=(s[0]<<16)|s[1]
        txt=s[2:]
        out=''.join('^%02X'%x if x<0x20 else (chr(CL[x-0x20]) if x-0x20<len(CL) else '?') for x in txt)
        print('    ID=%08X  text=%r'%(h,out))
