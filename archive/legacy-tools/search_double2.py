"""精准搜索：散文件(juiced/DLC) 与 patch.vpp_pc。
① 字面量 ascii "double"（整体匹配）；② 槽位相邻 双(619)胞(2158) 或 胞(2158)胎(2155) 或 双(619)胎(2155)。"""
import sys, os, glob, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def read_slots(buf, pos):
    n = len(buf); out=[]; i=pos
    while i+2 <= n:
        b0,b1 = buf[i],buf[i+1]
        if b0==0 and b1==0: return out
        out.append((b0<<8)|b1); i+=2
    return None

def iter_recs_raw(buf):
    bc,count,oa,offs = file_offsets(buf)
    seen=set()
    for off in offs:
        if off in seen: continue
        seen.add(off)
        if not (0 < off <= len(buf)-24): continue
        yield read_slots(buf, off+8)

def decode_mixed(buf, cl):
    out=[]
    for x in buf:
        if x < 0x100: out.append(chr(x))
        else:
            cp = cl.get(x)
            out.append(chr(cp) if cp else '\ufffd')
    return ''.join(out)

# charlist
v = Vpp(os.path.join(GAME,"patch.vpp_pc"))
e_cl = v.find("charlist_CH","txt")
cl_lines = v.read(e_cl).decode('utf-8').split('\n')
cl = {}
for i,s in enumerate(cl_lines):
    if s.strip().isdigit(): cl[i+0x20] = int(s)

def search_vpp(path, label):
    print("\n==== %s ====" % label)
    vv = Vpp(path)
    for e in vv.entries():
        if e['ext'] != 'le_strings': continue
        b = vv.read(e)
        for vals in iter_recs_raw(b):
            if not vals: continue
            s = decode_mixed(vals, cl)
            low = ''.join(chr(x) for x in vals if x<0x100).lower()
            if 'double' in low:
                # 只打印确实含有 "double" 字母序列的
                ascii_part = ''.join(chr(x) for x in vals if x<0x100)
                if 'double' in ascii_part.lower():
                    print("  [%s] %r" % (e['name'], s[:90]))
            # 槽位相邻检测
            for a,c in ((619,2158),(2158,2155),(619,2155)):
                if a in vals and c in vals:
                    print("  [相邻 %d-%d][%s] %r" % (a,c,e['name'],s[:90]))

def search_loose(path, label):
    print("\n==== %s ====" % label)
    if not os.path.exists(path):
        print("  (文件不存在)"); return
    buf = open(path,'rb').read()
    try:
        bc,count,oa,offs = file_offsets(buf)
    except Exception as ex:
        print("  (非 le_strings，跳过):", ex); return
    for vals in iter_recs_raw(buf):
        if not vals: continue
        s = decode_mixed(vals, cl)
        ascii_part = ''.join(chr(x) for x in vals if x<0x100).lower()
        if 'double' in ascii_part:
            print("  %r" % s[:90])
        for a,c in ((619,2158),(2158,2155),(619,2155)):
            if a in vals and c in vals:
                print("  [相邻 %d-%d] %r" % (a,c,s[:90]))

search_vpp(os.path.join(GAME,"patch.vpp_pc"), "patch.vpp_pc (全 le_strings)")

# DLC 散文件
for f in glob.glob(os.path.join(GAME,"DLC","**","*.le_strings"), recursive=True):
    search_loose(f, "DLC "+os.path.basename(f))
# juiced 散文件（Mods 与参考目录）
for f in glob.glob(r"F:\sr2-cn\**\*juiced*.le_strings", recursive=True):
    search_loose(f, "juiced "+f)
for f in glob.glob(os.path.join(GAME,"Mods","**","*.le_strings"), recursive=True):
    search_loose(f, "Mods "+os.path.basename(f))
