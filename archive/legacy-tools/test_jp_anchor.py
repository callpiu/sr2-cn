import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp = S.Vpp(game+"patch.vpp_pc")

def load_charlist(name):
    e = vp.find(name, "txt")
    if not e: 
        print("MISSING", name); return None
    buf = vp.read(e)
    m = re.search(rb'count=(\d+)', buf)
    start = m.end() if m else 0
    body = buf[start:]
    end = body.find(b'//ENDOFFILE')
    if end<0: end=len(body)
    cps = [int(x) for x in re.findall(rb'\d+', body[:end])]
    return cps

cl_ch = load_charlist("charlist_CH")
cl_jp = load_charlist("charlist_JP")
jpcl  = load_charlist("JPCharList")

print("charlist_CH count:", len(cl_ch))
print("charlist_JP count:", len(cl_jp) if cl_jp else None)
print("JPCharList  count:", len(jpcl) if jpcl else None)

# verify CH anchors
def cp_of(idx, cl): return cl[idx] if cl and idx < len(cl) else None
print("\n-- CH charlist spot checks --")
for ch in "你的弟兄们需要保护":
    print(ch, hex(ord(ch)), "idx in CH:", cl_ch.index(ord(ch)))

# anchors: HUD renders charlist_CH idx -> this garbled char
# intended charlist_CH idx -> we want to know which JP index holds the SAME intended character
# Garbled: 你->任 的->璨 弟->偶 兄->巧 们->位 需->雄 要->衡 保->伪 护->该
# So HUD glyph at (charlist_CH idx) = charlist_CH[jp_pos_of_that_char]
# i.e. if HUD font order == JP, then charlist_JP[ charlist_CH_idx ] should == codepoint of garbled char
mapping = {
 371:('你','任'), 1836:('的','璨'), 1067:('弟','偶'), 454:('兄','巧'),
 364:('们','位'), 2699:('需','雄'), 2328:('要','衡'), 423:('保','伪'), 1222:('护','该'),
}
print("\n-- TEST: is HUD font order == JP charlist? --")
for chidx,(intended,garb) in mapping.items():
    gcp = ord(garb)
    jp_at = cp_of(chidx, cl_jp)
    jpc_at = cp_of(chidx, jpcl)
    print(f"CHidx {chidx:4d} intended={intended}({ord(intended):#x}) garbled={garb}({gcp:#x}) | charlist_JP[{chidx}]={jp_at:#x if jp_at else None} JPCharList[{chidx}]={jpc_at:#x if jpc_at else None}")
