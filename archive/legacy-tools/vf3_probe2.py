import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"

def load_charlist(vp, name):
    e = vp.find(name, "txt")
    buf = vp.read(e)
    end = buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

vpatch = S.Vpp(game+"patch.vpp_pc")
vcommon = S.Vpp(game+"common.vpp_pc")
cl_ch = load_charlist(vpatch,"charlist_CH")
cl_jp = load_charlist(vpatch,"charlist_JP")

def dump_vf3(vp, name, cl, n=16):
    e = vp.find(name,"vf3_pc")
    buf = vp.read(e)
    cnt = struct.unpack_from('<I', buf, 8)[0]
    print(f"\n=== {name} count={cnt} ===")
    matches=0
    for k in range(min(n, cnt)):
        o = 0xD0 + k*16
        f = struct.unpack_from('<IIII', buf, o)
        note=""
        for fi,val in enumerate(f):
            if val in cl: note+=f" f{fi}={val:#06x}({chr(val)})"
        print(f"  glyph {k:4d} rec={f}{note}")
    # stats: how many records have a field equal to cl[k]?
    hit=0
    for k in range(cnt):
        o=0xD0+k*16; f=struct.unpack_from('<IIII',buf,o)
        if any(v==cl[k] for v in f): hit+=1
    print(f"  -> {hit}/{cnt} records have a field == charlist[{'CH' if cl is cl_ch else 'JP'}][k]")

dump_vf3(vpatch, "fnt_chinese", cl_ch)
dump_vf3(vcommon, "fnt_chinese", cl_ch)
