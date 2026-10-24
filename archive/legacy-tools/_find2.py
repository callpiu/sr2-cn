import glob, os

def search_bytes(path, seq):
    data=open(path,'rb').read()
    out=[]
    i=0
    while True:
        j=data.find(seq,i)
        if j<0: break
        out.append(j); i=j+1
    return data, out

# 1) static_CH LE grep
p=r"F:/sr2-cn/build_v21/static_CH.le_strings"
data, hits = search_bytes(p, "弟兄".encode('utf-16-le'))
print("static_CH LE 弟兄 hits:", len(hits))
if hits:
    for h in hits[:3]:
        seg=data[max(0,h-30):h+60].decode('utf-16-le','replace')
        print("   ...",seg,"...")
# also BE
_, h2 = search_bytes(p, "弟兄".encode('utf-16-be'))
print("static_CH BE 弟兄 hits:", len(h2))
# your/的 LE
_, h3 = search_bytes(p, "你的".encode('utf-16-le'))
print("static_CH LE 你的 hits:", len(h3))

print("\n=== English US files ASCII keyword search ===")
us_files=[
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/patch_us.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/juiced_US.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/dlc_us.le_strings",
]
KWS=[b'boys',b'protection',b'deal',b'attacked',b'your boys',b'getting hit',b'hit']
for f in us_files:
    if not os.path.exists(f): print("MISS",f); continue
    data=open(f,'rb').read()
    print("----",os.path.basename(f),"size",len(data))
    for kw in KWS:
        idx=0; c=0; ex=[]
        while True:
            j=data.find(kw,idx)
            if j<0: break
            c+=1
            if len(ex)<3:
                s=max(0,j-40); e=min(len(data),j+60)
                ex.append(data[s:e].decode('latin-1','replace'))
            idx=j+1
        if c: print(f"   {kw.decode()} : {c} hits  e.g. {ex}")
