import struct,hashlib
CL=[]
for l in open('F:/sr2-cn/_cl_now.txt','rb').read().decode('latin1').split('\n'):
    s=l.strip()
    if s.isdigit(): CL.append(int(s))
for ch in '市郊城区':
    print(ch, 'slot=%04X'%(CL.index(ord(ch))+0x20))
