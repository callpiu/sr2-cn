# -*- coding: utf-8 -*-
"""v534 = 干净 v532(641e5df5) + 弹药->填料（唯一新增修复）

剔除 v533 的 tagfix（去掉活动串 [format] 标签）—— 实测无效且会丢失绿色高亮，
属无效改动，不进发布包。
"""
import sys, struct, re, hashlib, shutil, os, datetime
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
SRC = game+"patch.vpp_pc.v532_before_exp.bak"      # 干净 v532
TMP = r"F:/sr2-cn/_v534_build.vpp_pc"              # 先在临时文件上改，验证后再部署

assert hashlib.md5(open(SRC,'rb').read()).hexdigest()=='641e5df5bf74383ffe47b795a9796210', "SRC 不是 v532"

shutil.copy2(SRC, TMP)
vp = S.Vpp(TMP)

def load_charlist(vp,name="charlist_CH"):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

cl=load_charlist(vp)
cp2ci={cp:i for i,cp in enumerate(cl)}
for ch in "填料":
    assert ord(ch) in cp2ci, f"{ch} 不在 charlist_CH"

ent=vp.find("static_CH","le_strings")
blob_start=vp.data_start+ent['body']
blob=bytes(vp.data[blob_start:blob_start+ent['size']])
magic,ver,buckets,count=struct.unpack_from('<IHHI',blob,0)
assert magic==0xA84C7F73
off=12+buckets*8
ptrs=[struct.unpack_from('<I',blob,off+i*4)[0] for i in range(count)]

TARGET=0x36B05984
recs=[o for o in ptrs if o+4<=len(blob) and ((struct.unpack_from('<HH',blob,o)[0]<<16)|struct.unpack_from('<HH',blob,o)[1])==TARGET]
print("hash 0x36B05984 记录数:",len(recs))
assert len(recs)==1
o=recs[0]
p=o+4; slots=[]
while True:
    s=struct.unpack_from('>H',blob,p)[0]
    if s==0: break
    slots.append(s); p+=2
cur="".join(chr(cl[s-0x20]) for s in slots)
print("改写前:",repr(cur))
assert cur=="弹药"

new_slots=[cp2ci[ord('填')]+0x20, cp2ci[ord('料')]+0x20]
abs_off=blob_start+o+4
# 前置断言：ID + 现文 + 终止符
assert bytes(vp.data[blob_start+o:blob_start+o+4])==struct.pack('<HH',0x36b0,0x5984), "ID mismatch"
old_bytes=b"".join(struct.pack('>H',s) for s in slots)
assert bytes(vp.data[abs_off:abs_off+4])==old_bytes, "slot bytes mismatch"
assert struct.unpack_from('>H',vp.data,abs_off+4)[0]==0, "missing terminator"
print("前置断言 OK;", old_bytes.hex(), "->", b"".join(struct.pack('>H',s) for s in new_slots).hex())

for i,s in enumerate(new_slots):
    struct.pack_into('>H', vp.data, abs_off+2*i, s)
open(TMP,'wb').write(bytes(vp.data))

# --- 写后验证（重新从磁盘加载）---
vp2=S.Vpp(TMP)
ent2=vp2.find("static_CH","le_strings")
bs2=vp2.data_start+ent2['body']
blob2=bytes(vp2.data[bs2:bs2+ent2['size']])
m2,v2,bk2,c2=struct.unpack_from('<IHHI',blob2,0)
assert m2==0xA84C7F73
o2=12+bk2*8
ptrs2=[struct.unpack_from('<I',blob2,o2+i*4)[0] for i in range(c2)]
found=None
for oo in ptrs2:
    if oo+4>len(blob2): continue
    i1,i2=struct.unpack_from('<HH',blob2,oo)
    if ((i1<<16)|i2)==TARGET:
        pp=oo+4; sl=[]
        while True:
            s=struct.unpack_from('>H',blob2,pp)[0]
            if s==0: break
            sl.append(s); pp+=2
        found="".join(chr(cl[s-0x20]) for s in sl)
print("改写后:",repr(found))
assert found=="填料"

# --- 差分断言：v532 -> v534 只应差 4 字节 ---
a=open(SRC,'rb').read(); b=open(TMP,'rb').read()
assert len(a)==len(b), (len(a),len(b))
diffpos=[i for i in range(len(a)) if a[i]!=b[i]]
print(f"差异字节数: {len(diffpos)}  位置: {[hex(x) for x in diffpos]}")
assert len(diffpos)==4, "差异不是 4 字节，异常！"
print("v534 md5:", hashlib.md5(b).hexdigest())
print("BUILD OK ->", TMP)
