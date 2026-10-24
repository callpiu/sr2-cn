# -*- coding: utf-8 -*-
"""回滚清单可行性核查：
   1) 兄弟帮 -> 兄弟会
   2) 指定辩护人 -> 指定辩护律师
   3) 子弹 弹药 霰弹枪（"霰"坏字位？需确认）
   4) 3王 -> 三王
   每条：查现态、查字数、查字表可用性、查等长方案"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()
CL=[]
for l in open(r'F:\sr2-cn\_juice_fix\charlist_CH.txt',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('//') or l.startswith('#'): continue
    CL.append(int(l))
IDX={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
def s(ch):
    cp=ord(ch)
    return IDX[cp]+0x20 if cp in IDX else None

SEG=[(0x1C00000,0x1C80000,'A'),(0x2E00000,0x2E40000,'B')]
recs=[]
for lo,hi,nm in SEG:
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            q=p;slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            recs.append((p,nm,slots,''.join(dec(x) for x in slots)))
            p=q+2
        else: p+=2
print('总记录 %d'%len(recs))
print()

def scan(key,label,maxshow=25):
    print('='*72)
    print('【%s】搜索 %r'%(label,key))
    hits=[r for r in recs if key in r[3]]
    print('  命中 %d 条'%len(hits))
    seen=set();n=0
    for p,nm,slots,t in hits:
        if t in seen: continue
        seen.add(t)
        if len(t)>60: continue
        print('   @0x%08X [%s] %2d字 %r'%(p,nm,len(t),t))
        n+=1
        if n>=maxshow: break
    if len(seen)>n: print('   ...(共 %d 种不同文本)'%len(seen))
    return hits

scan('兄弟帮','兄弟帮')
print()
scan('辩护','指定辩护人')
print()
scan('霰弹','霰弹枪')
print()
scan('3王','3王')
print()
print('='*72)
print('=== 字表可用性检查 ===')
for kw in ['兄弟会','指定辩护律师','霰弹枪','三王']:
    miss=[c for c in kw if s(c) is None]
    print('  %-8r %d字  缺字=%s  slots=%s'%(kw,len(kw),miss or '无',
        ' '.join('%s:%04X'%(c,s(c)) for c in kw if s(c))))
print()
print('=== 等长性对比 ===')
for old,new in [('兄弟帮','兄弟会'),('指定辩护人','指定辩护律师'),('霰弹枪','霰弹枪'),('3王','三王')]:
    print('  %-10s(%d字) -> %-12s(%d字)  %s'%(old,len(old),new,len(new),
      '✓等长' if len(old)==len(new) else '✗不等长，长%+d'%(len(new)-len(old))))