# -*- coding: utf-8 -*-
"""核心洞察：HUD正常 + 字幕乱码 → 不是字符表问题，是"字幕通路"问题。
活动字幕走 voice_script_CH。检查它与 static_CH 的 slot 编码是否一致。
"""
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
CL=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]

def recs(raw):
    magic,ver,buckets,count=struct.unpack_from('<IHHI',raw,0)
    oa=16+buckets*8
    d={}
    order=[]
    for i in range(count):
        o=struct.unpack_from('<I',raw,oa+i*4)[0]
        if not(0<=o<len(raw)-4):continue
        h=struct.unpack_from('<H',raw,o)[0]
        p=o+4; us=[]
        while p+1<len(raw):
            u=struct.unpack_from('>H',raw,p)[0]; p+=2
            if u==0:break
            us.append(u)
        d.setdefault(h,us); order.append(h)
    return d,order

def dec(units, delta=32):
    out=[]
    for u in units:
        if u<0x100: out.append(chr(u))
        else:
            i=u-delta
            out.append(chr(CL[i]) if 0<=i<len(CL) else '{?%d}'%u)
    return ''.join(out)

VS,_=recs(v.read(v.find('voice_script_CH','le_strings')))
ST,_=recs(v.read(v.find('static_CH','le_strings')))
print("voice_script_CH 记录数 =", len(VS))
print("static_CH 记录数 =", len(ST))
print()
# 找直升机突击字幕
h_key=0xEC7A
if h_key in VS: print("★ VS h=EC7A:", dec(VS[h_key]))
if h_key in ST: print("★ ST h=EC7A:", dec(ST[h_key]))
print()
# 找 "你的弟兄们需要你的保护" 类文本
for name,D in [('static_CH',ST),('voice_script_CH',VS)]:
    hits=[]
    for h,us in D.items():
        s=dec(us)
        if '弟兄' in s or '保护' in s or '直升' in s:
            hits.append((h,s))
    print("[%s] 命中 %d 条:" % (name,len(hits)))
    for h,s in hits[:10]:
        print("   h=%04X  %s" % (h,s[:70]))
    print()
