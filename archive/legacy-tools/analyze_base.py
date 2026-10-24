import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

VANILLA = r"F:\sr2-cn\_day_2026-10-07\07_备份快照\patch.vpp_pc.原版_能跑_2320.bak"
LOCAL  = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
BASE = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def get_cl(path):
    v = Vpp(path); e = v.find("charlist_CH","txt")
    nums=[int(x) for x in v.read(e).decode('utf-8','replace').split() if x.strip().lstrip('-').isdigit()]
    return nums[1:] if nums and nums[0]==len(nums)-1 else nums

cl_trad=get_cl(VANILLA); cl_simp=get_cl(LOCAL)
rev_trad={i+SHIFT:chr(c) for i,c in enumerate(cl_trad)}
rev_simp={i+SHIFT:chr(c) for i,c in enumerate(cl_simp)}

def stats(d, revmap, count):
    buckets,cnt,off_at,offs=file_offsets(d)
    ok=bad=0; bad_samples=[]
    for off in dict.fromkeys(offs):
        if not (0<off<=len(d)-10): continue
        units,_=read_units(d,off+8)
        if units is None: continue
        recbad=False
        for vv,_ in units:
            if vv>=0x100 and not (0<=vv-SHIFT<count): recbad=True; break
        if recbad:
            bad+=1
            if len(bad_samples)<2:
                t=[chr(vv) if vv<0x100 else revmap.get(vv,'\ufffd') for vv,_ in units]
                bad_samples.append(''.join(t)[:50])
        else: ok+=1
    return ok,bad,bad_samples

# 收集所有 vpp（游戏顶层 + DLC 递归）
vpp_paths=[]
for f in os.listdir(BASE):
    if f.lower().endswith('.vpp_pc') and f.lower()!='patch.vpp_pc':
        vpp_paths.append(os.path.join(BASE,f))
for root,_,fs in os.walk(os.path.join(BASE,'DLC')):
    for f in fs:
        if f.lower().endswith('.vpp_pc'):
            vpp_paths.append(os.path.join(root,f))
print("找到 VPP 数: %d" % len(vpp_paths))

for p in sorted(vpp_paths):
    try: v=Vpp(p)
    except Exception as ex:
        print("打开失败 %s: %s" % (p,ex)); continue
    entries=[e for e in v.entries() if e['ext']=='le_strings']
    if not entries: continue
    short=os.path.relpath(p,BASE)
    for e in entries:
        d=v.read(e)
        if struct.unpack_from('<I',d,0)[0]!=0xA84C7F73: continue
        ok_t,bad_t,_=stats(d,rev_trad,len(cl_trad))
        ok_s,bad_s,samp_s=stats(d,rev_simp,len(cl_simp))
        flag=""
        if bad_s>bad_t: flag="★简表更多越界(嫌疑)"
        elif bad_t==0 and bad_s==0: flag="两表OK"
        print("%-50s 繁OK=%5d BAD=%4d | 简OK=%5d BAD=%4d  %s" %
              (short+"::"+e['name'], ok_t,bad_t,ok_s,bad_s,flag))
        if bad_s>bad_t:
            for s in samp_s: print("     越界样本: %s" % s)
