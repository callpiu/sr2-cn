import glob, os, struct

# UTF-16BE byte sequences for keywords
KW = {
 '弟兄':'\u5f1f\u5144', '兄弟':'\u5144\u5f1f',
 '保護':'\u4fdd\u8b77', '保护':'\u4fdd\u62a4',
 '襲擊':'\u8972\u64ca', '袭击':'\u88ad\u51fb',
 '免遭':'\u514d\u906d', '生意':'\u751f\u610f',
}
def be(s): return s.encode('utf-16-be')

files = []
for p in glob.glob(r"F:/sr2-cn/build_v*/static_CH.le_strings"): files.append(p)
files += [
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/patch_ch.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/juiced_CH.le_strings",
 r"G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/dlc_ch.le_strings",
]
# also other CH in build_v
for p in glob.glob(r"F:/sr2-cn/build_v*/*_CH.le_strings"): 
    if p not in files: files.append(p)

for p in files:
    data=open(p,'rb').read()
    hits=[]
    for name,kw in KW.items():
        b=be(kw)
        idx=0
        while True:
            i=data.find(b,idx)
            if i<0: break
            hits.append((i,name)); idx=i+1
    if hits:
        print("==== ",os.path.basename(p),"size",len(data),"hits",len(hits))
        hits.sort()
        # decode entries around hits
        for i,name in hits[:6]:
            # find entry start: scan backwards to a 4-byte aligned crc? just decode window
            s=max(0,i-40); e=min(len(data),i+120)
            seg=data[s:e]
            # try decode utf16-be from s
            txt=seg.decode('utf-16-be','replace')
            print(f"   [{name}] @{i}: ...{txt}...")
