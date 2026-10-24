import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
files={
 "v407(before)": game+"patch.vpp_pc.beforescrapyardfix.bak",
 "v532(clean)":  game+"patch.vpp_pc.v532_before_exp.bak",
}
def load_charlist(vp,name="charlist_CH"):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

def all_texts(vp):
    cl=load_charlist(vp)
    ent=vp.find("static_CH","le_strings"); data=vp.read(ent)
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    assert magic==0xA84C7F73
    off=12+buckets*8
    ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
    out=[]
    for o in ptrs:
        if o+4>len(data): continue
        p=o+4; ch=[]
        while p+1<len(data):
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            p+=2; ci=s-0x20
            ch.append(chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD')
        out.append("".join(ch))
    return out, (buckets,count)

probes=[
 ("拆车厂A(交付d/d/辆...清单)", lambda t: "交付" in t and "%d/%d" in t and "%ls" in t and t.index("%d")<t.index("%ls")),
 ("拆车厂B(赚到$%i在%ls前)", lambda t: "赚到了" in t and "%i" in t and "%ls" in t and t.index("赚到")<t.index("%ls")),
 ("圣徽街(4条)", lambda t: "圣徽街" in t),
 ("兄弟帮任务N", lambda t: "兄弟帮任务" in t),
 ("散筒枪", lambda t: "散筒枪" in t),
 ("火料", lambda t: "火料" in t),
 ("投掷类", lambda t: "投掷类" in t),
 ("等候主机玩家", lambda t: "等候主机玩家" in t),
 ("弹药(应仍为弹药)", lambda t: "弹药" in t),
 ("旧值-圣徒街", lambda t: t=="圣徒街"),
 ("旧值-兄弟会任务", lambda t: "兄弟会任务" in t),
 ("旧值-霰弹枪", lambda t: "霰弹枪" in t),
 ("旧值-已扔出", lambda t: "已扔出" in t),
 ("旧值-等待主机玩家", lambda t: t=="等待主机玩家"),
]
res={}
for label,path in files.items():
    vp=S.Vpp(path)
    texts,(bk,cnt)=all_texts(vp)
    print(f"\n===== {label}  static_CH buckets={bk} count={cnt} records={len(texts)} =====")
    for name,fn in probes:
        n=sum(1 for t in texts if fn(t))
        res[(label,name)]=n
        print(f"   {name:28s}: {n}")
    del vp
