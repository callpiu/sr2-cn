# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0,'.')
from _vpp import Vpp
gv=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))

pairs=[('你',371,336),('的',1836,1784),('弟',1035,410),('兄',422,967),('们',332,362),
       ('需',2667,2656),('要',2296,2268),('保',391,354),('护',1190,2342)]

def rank_by(keyfunc, name):
    items=[]
    for i,c in enumerate(cl):
        k=keyfunc(c)
        if k is None: continue
        items.append((k,i,c))
    items.sort()
    rank={c:i for i,(k,orig,c) in enumerate(items)}
    idxs=[rank.get(ord(ch),-1) for ch,_,_ in pairs]
    obs=[o for _,_,o in pairs]
    match=sum(1 for a,b in zip(idxs,obs) if a==b)
    print(f'{name:24s} match={match}/9  idxs={idxs}')
    return idxs

print('observed:                 ', [o for _,_,o in pairs])
print('codepoint(原始):          ', [i for _,i,_ in pairs])
def gbk(c):
    try: return chr(c).encode('gbk')
    except: return None
def gb2312(c):
    try: return chr(c).encode('gb2312')
    except: return None
def utf8(c):
    try: return chr(c).encode('utf-8')
    except: return None
rank_by(gbk, 'sort by GBK bytes')
rank_by(gb2312, 'sort by GB2312 bytes')
rank_by(utf8, 'sort by UTF-8 bytes')
rank_by(lambda c: -c, 'sort by codepoint DESC')
rank_by(lambda c: c & 0xFF, 'sort by codepoint low byte')
rank_by(lambda c: (c & 0xFF, c), 'sort by low byte then cp')

# 也测: 在“仅CJK”子集中的名次
def rank_cjk(keyfunc, name):
    items=[(keyfunc(c),i,c) for i,c in enumerate(cl) if c>0x2E80]
    items.sort()
    rank={c:i for i,(k,orig,c) in enumerate(items)}
    idxs=[rank.get(ord(ch),-1) for ch,_,_ in pairs]
    obs=[o for _,_,o in pairs]
    m=sum(1 for a,b in zip(idxs,obs) if a==b)
    print(f'{name:24s} match={m}/9  idxs={idxs}')
rank_cjk(gbk, 'CJK-only by GBK')
rank_cjk(lambda c:c, 'CJK-only by codepoint')
