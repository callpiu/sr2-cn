import sys
sys.path.insert(0,"F:/sr2-cn")
from sr2font import Vpp
v=Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
import re
def find_markup(name):
    e=v.find(name,'le_strings'); 
    if not e: return []
    d=v.read(e)
    # decode as utf-16-le (string pool), find [color / [format / closers
    txt=d.decode('utf-16-le','ignore')
    return re.findall(r'\[/?[a-zA-Z]+[^\]\x00]{0,16}\]', txt)
for f in ['static_US','voice_script_US','platform_PC_US']:
    tags=find_markup(f)
    from collections import Counter
    c=Counter(t for t in tags if 'color' in t.lower() or 'format' in t.lower())
    if c:
        print(f, dict(c))
# show one full example containing [color
e=v.find('voice_script_US','le_strings')
d=v.read(e).decode('utf-16-le','ignore')
i=d.find('[color')
print("\nexample:", repr(d[max(0,i-30):i+50]) if i>=0 else "none in voice_script_US")
e=v.find('static_US','le_strings')
d=v.read(e).decode('utf-16-le','ignore')
i=d.lower().find('[color')
print("static_US example:", repr(d[max(0,i-40):i+60]) if i>=0 else "none")
