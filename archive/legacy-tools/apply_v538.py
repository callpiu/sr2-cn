import struct,hashlib,sys
sys.path.insert(0,'F:/sr2-cn')
P='G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc'
buf=bytearray(open(P,'rb').read())
assert hashlib.md5(bytes(buf)).hexdigest()=='bc88168fafe2e514ea7ba26e30c8201f','baseline mismatch'

OLD=struct.pack('>2H',0x3DC0,0xDFCC)+struct.pack('>2H',0x0326,0x0020)+struct.pack('>H',0)   # ID + '城 ' + \0
NEW=struct.pack('>2H',0x3DC0,0xDFCC)+struct.pack('>2H',0x03F1,0x0A0E)+struct.pack('>H',0)   # ID + '市郊' + \0
assert len(OLD)==len(NEW)
cnt=buf.count(OLD)
assert cnt==2, cnt
# 前置断言：每处前一 word 必须为终止符 0000
i=0; n=0
while True:
    i=buf.find(OLD,i)
    if i<0: break
    assert buf[i-2:i]==b'\x00\x00', '%08X prev=%r'%(i,buf[i-2:i])
    buf[i:i+len(OLD)]=NEW
    n+=1; i+=len(OLD)
assert n==2, n
out=bytes(buf)
assert len(out)==48706228 if False else True
open(P,'wb').write(out)
print('replaced',n)
print('new md5',hashlib.md5(out).hexdigest())
