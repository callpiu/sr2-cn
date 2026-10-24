import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")

def load_charlist(name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE'); 
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

cl=load_charlist("charlist_CH")
cljp=load_charlist("charlist_JP")
jpcl=load_charlist("JPCharList")
cp2ci={cp:i for i,cp in enumerate(cl)}

# permutation anchors: intended charlist_CH index -> garbled char
# from alignment of clean decode + user garbled
rec1_pairs=[(371,'任'),(1836,'璨'),(1035,'偶'),(422,'巧'),(332,'位'),(2667,'雄'),(2296,'衡'),(371,'任'),(1836,'璨'),(391,'伪'),(1190,'该')]
rec2_pairs=[(371,'任'),(1836,'璨'),(1035,'偶'),(422,'巧'),(332,'位'),(2296,'衡'),(478,'校'),(581,'勾'),(2357,'远'),(470,'藐'),(1963,'乱'),(1792,'携'),(1127,'伪'),(2790,'该'),(391,'亡'),(1190,'位'),(324,'通'),(332,'像'),(428,'匪'),(2531,'冰'),(2280,'挺'),(479,'拮')]

allpairs=dict(rec1_pairs+rec2_pairs)  # ci -> garbled char

print("ci -> garbled -> garbled_CHidx -> codepoint")
for ci,g in sorted(allpairs.items()):
    gci=cp2ci[ord(g)]
    print(f"  {ci:4d} -> {g}(ci{gci}, {ord(g):#x})  charlist_JP[{ci}]={cljp[ci] if ci<len(cljp) else 'OOB':#x} JPCharList[{ci}]={jpcl[ci] if ci<len(jpcl) else 'OOB':#x}")

print("\n-- test charlist_JP[ci]==ord(garbled)? --")
ok=sum(1 for ci,g in allpairs.items() if ci<len(cljp) and cljp[ci]==ord(g))
print(f"  JP matches {ok}/{len(allpairs)}")
print("-- test JPCharList[ci]==ord(garbled)? --")
ok=sum(1 for ci,g in allpairs.items() if ci<len(jpcl) and jpcl[ci]==ord(g))
print(f"  JPCharList matches {ok}/{len(allpairs)}")

# test affine: garbled_CHidx = A*ci + B  (mod len(cl))?  compute via first few
print("\n-- affine test on garbled_CHidx vs ci (using pairs) --")
pts=[(ci, cp2ci[ord(g)]) for ci,g in allpairs.items()]
for (ci1,b1),(ci2,b2) in [(pts[0],pts[1]),(pts[0],pts[2]),(pts[1],pts[2])]:
    if ci2!=ci1:
        A=(b2-b1)/(ci2-ci1)
        B=b1-A*ci1
        print(f"  using ({ci1},{b1})&({ci2},{b2}): A={A:.3f} B={B:.1f}")
