import os
D=r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings"
cxt=os.path.join(D,"juiced_CH.cxt")
les=os.path.join(D,"juiced_CH.le_strings")

raw=open(cxt,'rb').read()
print("cxt size",len(raw))
print("first 4 bytes:",raw[:4].hex(' '))
print("BOM utf8?", raw[:3]==b'\xef\xbb\xbf')
print("last 40 bytes:",raw[-40:].hex(' '))
try:
    raw.decode('utf-8'); print("decodes as utf-8: YES")
except Exception as e:
    print("utf-8 decode err:",e)
print("ends with newline?", raw.endswith(b'\n'), " count \\n:", raw.count(b'\n'), " count \\r:", raw.count(b'\r'))
# check for existing color/format tags in US cxt
us=open(os.path.join(D,"juiced_US.cxt"),encoding='utf-8').read()
print("\nUS cxt has '[color'?", '[color' in us, " '[format'?", '[format' in us, " 'ACT_HELI'?", 'ACT_HELI' in us)

# does le_strings contain compiled cxt content?
ld=open(les,'rb').read()
print("\nle_strings size",len(ld), "mtime", os.path.getmtime(les), "cxt mtime", os.path.getmtime(cxt))
for kw in ['J_OPTIONS','J_UNCFPS','ACT_HELI','弟兄','homies','J_BETTERAO']:
    hit = kw.encode('utf-16-le') in ld or kw.encode('utf-16-be') in ld or kw.encode('utf-8') in ld
    print(f"  le_strings contains {kw!r}? {hit}")
