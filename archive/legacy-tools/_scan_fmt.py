import sys
sys.path.insert(0,"F:/sr2-cn")
from sr2font import Vpp

v=Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
files={'static_CH':'static_CH','static_US':'static_US',
       'voice_script_CH':'voice_script_CH','voice_script_US':'voice_script_US'}
data={}
for nm,key in files.items():
    e=v.find(nm,'le_strings')
    if not e:
        print("NOT FOUND",nm); continue
    data[key]=v.read(e)
    print(nm,"size",len(data[key]))

def scan(d, probe_bytes_list, label):
    for pb in probe_bytes_list:
        for off in range(4):
            idx=d.find(pb, off)
            if idx>=0:
                # show context
                s=max(0,idx-20); e=min(len(d),idx+60)
                print(f"  [{label}] found align {off} : {d[s:e]!r}")
                return True
    return False

print("\n--- static_CH scan for 弟兄 (BE/LE) ---")
scan(data.get('static_CH',b''), ["弟兄".encode('utf-16-be'),"弟兄".encode('utf-16-le'),"兄弟".encode('utf-16-be'),"兄弟".encode('utf-16-le')], "CH")
print("--- static_US scan for boys (BE/LE) ---")
scan(data.get('static_US',b''), [b'b\x00o\x00y\x00s\x00', b'\x00b\x00o\x00y\x00s', b'boys'], "US")
print("--- voice_script_CH scan for 弟兄 ---")
scan(data.get('voice_script_CH',b''), ["弟兄".encode('utf-16-be'),"弟兄".encode('utf-16-le'),"兄弟".encode('utf-16-be'),"兄弟".encode('utf-16-le')], "VCH")
print("--- voice_script_US scan for boys ---")
scan(data.get('voice_script_US',b''), [b'b\x00o\x00y\x00s\x00', b'\x00b\x00o\x00y\x00s', b'boys'], "VUS")
