import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
BAK = game+"patch.vpp_pc.v532_before_exp.bak"
vp = S.Vpp(BAK)

def load_charlist(name):
    e = vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

cl = load_charlist("charlist_CH")

ent = vp.find("static_CH","le_strings")
data = vp.read(ent)
magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
print("magic",hex(magic),"ver",ver,"buckets",buckets,"count",count)
assert magic==0xA84C7F73

btab_off = 12
ptrs = []
off = btab_off + buckets*8
assert off + count*4 <= len(data), (off, count*4, len(data))
for i in range(count):
    ptrs.append(struct.unpack_from('<I', data, off+i*4)[0])

def decode_record(off):
    id1,id2 = struct.unpack_from('<HH', data, off)
    p = off+4
    chars=[]; slots=[]
    while True:
        s = struct.unpack_from('>H', data, p)[0]
        if s==0: break
        slots.append(s); p+=2
        ci = s-0x20
        c = chr(cl[ci]) if 0<=ci<len(cl) else '?'
        chars.append((c,ci,s))
    return (id1,id2), chars, slots

targets = [0x84F287ED, 0x10AF1E62]
for t in targets:
    found=False
    for off in ptrs:
        (id1,id2),chars,slots = decode_record(off)
        h=(id1<<16)|id2
        if h==t:
            found=True
            cjk=[(c,ci,s) for (c,ci,s) in chars if ci>=95]
            print(f"\n=== hash {t:#010x} ===")
            print(" full:", "".join(c for c,ci,s in chars))
            print(" CJK (%d):"%len(cjk), " ".join(f"{c}(ci{ci},s{s})" for c,ci,s in cjk))
            break
    if not found: print("NOT FOUND",hex(t))
