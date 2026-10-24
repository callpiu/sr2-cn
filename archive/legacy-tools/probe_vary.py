# -*- coding: utf-8 -*-
"""活动串【变长】探针 —— 决定性实验

★ 为什么必须变长：之前所有实验（ASCII/25条打标/车耐久）都是【等长替换+空格补齐】，
  屏幕上的字数永远是 11/22，因此"字幕没变化"这个观察【没有判别力】。
  本次把 REC1 改成 3 个字，若屏幕字数从 11 变成 3 → 就是这条记录；
  若仍是 11 个乱码 → 才是真的来自别处。

用法：
  python probe_vary.py apply     # 改成 3 字探针（自动备份）
  python probe_vary.py restore   # 还原到 apply 前的备份
  python probe_vary.py show      # 只看当前内容
"""
import sys, struct, re, os, shutil, hashlib, datetime
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
PATH=game+"patch.vpp_pc"
TARGETS={0x84F287ED:"REC1", 0x10AF1E62:"REC2"}
PROBE_TEXT={0x84F287ED:"一二三"}          # 3 个字，极醒目（壹贰叁 不在字表）

def load_charlist(vp):
    buf=vp.read(vp.find("charlist_CH","txt"))
    end=buf.find(b'//ENDOFFILE')
    return [int(x) for x in re.findall(rb'\d+', buf[:end if end>0 else len(buf)])]

def read_table(vp):
    cl=load_charlist(vp)
    ent=vp.find("static_CH","le_strings")
    data=bytes(vp.read(ent))
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    assert magic==0xA84C7F73
    VER=ver
    btab_off=12; ptr_off=12+buckets*8
    buckets_raw=[struct.unpack_from('<II',data,btab_off+i*8) for i in range(buckets)]
    ptrs=[struct.unpack_from('<I',data,ptr_off+i*4)[0] for i in range(count)]
    recs=[]
    for o in ptrs:
        id1,id2=struct.unpack_from('<HH',data,o)
        p=o+4; slots=[]
        while True:
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            slots.append(s); p+=2
        recs.append(((id1<<16)|id2, slots))
    return cl,ent,data,buckets,count,buckets_raw,ptrs,recs,VER

def decode(slots,cl):
    return "".join(chr(cl[s-0x20]) if 0<=s-0x20<len(cl) else '?' for s in slots)

def show():
    vp=S.Vpp(PATH); cl,ent,data,bk,cnt,bt,ptrs,recs,VER=read_table(vp)
    print(f"patch md5={hashlib.md5(open(PATH,'rb').read()).hexdigest()}")
    print(f"static_CH buckets={bk} count={cnt}")
    for h,slots in recs:
        if h in TARGETS:
            t=decode(slots,cl); n=len([c for c in t if ord(c)>0x2000])
            print(f"  {TARGETS[h]} {h:#010x} CJK={n}: {t.rstrip()!r}")

def apply_probe():
    vp=S.Vpp(PATH); cl,ent,data,bk,cnt,bt,ptrs,recs,VER=read_table(vp)
    cp2slot={cp:i+0x20 for i,cp in enumerate(cl)}
    newrecs=[]
    changed=0
    for h,slots in recs:
        if h in PROBE_TEXT:
            txt=PROBE_TEXT[h]
            for ch in txt: assert ord(ch) in cp2slot, f"{ch} 不在字表"
            newslots=[cp2slot[ord(ch)] for ch in txt]
            print(f"  {TARGETS[h]} {h:#010x}: {decode(slots,cl).rstrip()!r} -> {txt!r}")
            newrecs.append((h,newslots)); changed+=1
        else:
            newrecs.append((h,slots))
    assert changed==len(PROBE_TEXT), "未找到全部目标记录"

    # 重建 blob：记录顺序 & 桶划分完全不变，只改文本长度 -> 重算指针与桶 addr
    HDR=12; BTAB=8*bk
    body=bytearray()
    rec_off=[]
    for h,slots in newrecs:
        rec_off.append(len(body))
        body+=struct.pack('<HH', h>>16, h&0xFFFF)
        for s in slots: body+=struct.pack('>H',s)
        body+=b'\x00\x00'
    ptr_abs=[HDR+BTAB+cnt*4+o for o in rec_off]
    out=bytearray()
    out+=struct.pack('<IHHI',0xA84C7F73,VER,bk,cnt)
    # 桶表：count 沿用，addr = 该桶第一条记录对应的指针项绝对地址
    # 桶是按记录顺序连续切分的，沿用原 bucket count 序列即可
    idx=0
    for bcnt,_ in bt:
        addr = HDR+BTAB+idx*4 if bcnt>0 else 0
        out+=struct.pack('<II',bcnt,addr)
        idx+=bcnt
    for p in ptr_abs: out+=struct.pack('<I',p)
    out+=body
    assert idx==cnt, (idx,cnt)

    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak=PATH+f".v{ts}_before_varyprobe.bak"
    shutil.copy2(PATH,bak)
    vp.replace_body_appended(ent, bytes(out), align=0x800)
    open(PATH,'wb').write(bytes(vp.data))
    print("备份:",bak)
    print("新 md5:",hashlib.md5(open(PATH,'rb').read()).hexdigest())
    print("\n>>> 请启动游戏，进入直升机突击活动，看那条字幕现在显示【几个字】")
    print("    若显示 3 个字 -> 字幕就是 REC1（之前'没变化'是观察/加载问题）")
    print("    若仍是 11 个乱码 -> 字幕真的来自别处")
    print("    看完后运行: python probe_vary.py restore")

def restore():
    baks=sorted([f for f in os.listdir(game) if f.startswith("patch.vpp_pc.v") and f.endswith("_before_varyprobe.bak")])
    if not baks: print("没有探针备份"); return
    bak=game+baks[-1]
    shutil.copy2(bak,PATH)
    print("已还原:",baks[-1])
    show()

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "show"
    {"show":show,"apply":apply_probe,"restore":restore}[cmd]()
