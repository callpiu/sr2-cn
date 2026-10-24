"""定位并解码 patch.vpp_pc/Item_text 里 DRUG_TWIN_DESC 的当前译文。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl = v.find("charlist_CH","txt")
cl_lines = v.read(e_cl).decode('utf-8').split('\n')
cl = {}
for i,s in enumerate(cl_lines):
    if s.strip().isdigit(): cl[i+0x20] = int(s)

def read_slots(buf, pos):
    n=len(buf); out=[]; i=pos
    while i+2<=n:
        b0,b1=buf[i],buf[i+1]
        if b0==0 and b1==0: return out
        out.append((b0<<8)|b1); i+=2
    return None

def decode(vals):
    o=[]
    for x in vals:
        if x<0x100: o.append(chr(x))
        else:
            cp=cl.get(x); o.append(chr(cp) if cp else '\ufffd')
    return ''.join(o)

# 找 Item_text 条目
for e in v.entries():
    if e['name'].lower()=='item_text':
        ent=e; break
else:
    print("Item_text 未找到"); sys.exit(1)

b = v.read(ent)
print("Item_text ext=%s size=%d" % (ent['ext'], ent['size']))
body_off = v.data_start + ent['body']

# 该表可能不是 le_strings 格式（可能是 xml/xtbl）。先判断 magic
magic = struct.unpack_from('<I', b, 0)[0]
print("magic=%08x (A84C7F73=le_strings)" % magic)

if magic == 0xA84C7F73:
    bc,count,oa,offs = file_offsets(b)
    print("buckets=%d count=%d" % (bc,count))
    # le_strings 用 hash 索引，无明文 key。但 blob 里含明文 'DRUG_TWIN_DESC'?
    # 实际上若 Item_text 是 le_strings，key 明文不该出现。之前 find_twin_desc 报"含明文 key"
    # 说明 Item_text 里确实有 'DRUG_TWIN_DESC' 明文 —— 那它多半是 xtbl/xml 明文表。
    print("blob 中 DRUG_TWIN_DESC 出现次数:", b.count(b'DRUG_TWIN_DESC'))
    idx = b.find(b'DRUG_TWIN_DESC')
    print("首次出现 @0x%X" % idx)
    print("上下文:", b[max(0,idx-40):idx+80])
