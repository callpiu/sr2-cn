"""定位 DRUG_TWIN_DESC：在游戏所有 vpp_pc 的 le_strings 里找 key=DRUG_TWIN_DESC 的记录，
并解码出当前译文（确认是否=双胞胎）。同时列出其它 *_TWIN_* / DOUBLE 相关键。"""
import sys, os, glob, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v0 = Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl = v0.find("charlist_CH","txt")
cl_lines = v0.read(e_cl).decode('utf-8').split('\n')
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

# DRUG_TWIN_DESC 作为 le_strings 的 hash 或 key？le_strings 用 u64 hash 索引，不存 key 明文。
# 所以我们反向：哈希无法直接匹配 key，改为直接搜「双胞胎」三字在 patch 内（应该找不到），
# 并把 liquor_store 用的这批 DRUG_* DESC key 列出来，看看哪个译文可能是「双胞胎」。
# 策略：找 patch.vpp_pc 里所有 _CH le_strings 记录，列出含「双」或「胞」「胎」的；已知搜不到双胞胎。
# 因此更好办法：Juiced 读取这些描述是从 le_strings 的 hash。需计算 DRUG_TWIN_DESC 的 hash。

# 先确认：DRUG_TWIN 等 key 是否作为 ascii 明文存在于某个 le_strings（有些表 key 明文存储）
print("=== 在所有 vpp 内搜 ascii key 'DRUG_TWIN_DESC' / 'TWIN_DESC' 明文 ===")
for path in glob.glob(os.path.join(GAME,"*.vpp_pc")):
    try: v=Vpp(path)
    except: continue
    for e in v.entries():
        blob=v.read(e)
        if b'DRUG_TWIN_DESC' in blob or b'TWIN_DESC' in blob:
            print("  [%s|%s] 含明文 key" % (os.path.basename(path), e['name']))
