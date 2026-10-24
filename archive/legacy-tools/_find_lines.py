import struct, sys, glob, os

def parse(path):
    with open(path,'rb') as f:
        data=f.read()
    # detect possible 4-byte header (entry count)
    # try parse assuming entries start at 0
    def try_parse(off):
        entries=[]; i=off; n=len(data)
        while i+6<=n:
            crc=struct.unpack_from('<I',data,i)[0]
            j=i+4; chars=[]
            while j+2<=n:
                ch=struct.unpack_from('>H',data,j)[0]
                if ch==0: break
                chars.append(ch); j+=2
            else:
                return None
            text=''.join(chr(c) for c in chars)
            entries.append((crc,text))
            i=j+2
            if i>=n: break
        return entries
    # try offset 0 and 4
    for off in (0,4):
        e=try_parse(off)
        if e and any(any(ord(c)>0x2E80 for c in t) for _,t in e[:20]):
            return e
    return try_parse(0) or []

KW=('弟兄','兄弟','保護','保护','襲擊','袭击','談幾','谈几','生意','免遭')
files=[
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/patch_ch.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/juiced_CH.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/dlc_ch.le_strings",
]
# also scan build_v folders static_CH
for p in glob.glob(r"F:/sr2-cn/build_v*/static_CH.le_strings"):
    files.append(p)

for p in files:
    if not os.path.exists(p): 
        print("MISSING",p); continue
    print("==== ",p)
    try:
        es=parse(p)
    except Exception as ex:
        print("  parse err",ex); continue
    print("  entries:",len(es))
    for crc,t in es:
        if any(k in t for k in KW):
            print(f"  CRC={crc:08X}  {t!r}")
