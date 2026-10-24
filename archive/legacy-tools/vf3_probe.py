import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S

game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"

def load_charlist(vp, name):
    e = vp.find(name, "txt")
    buf = vp.read(e)
    m = re.search(rb'count=(\d+)', buf); start = m.end()
    body = buf[start:]; end = body.find(b'//ENDOFFILE')
    if end<0: end=len(body)
    return [int(x) for x in re.findall(rb'\d+', body[:end])]

vpatch = S.Vpp(game+"patch.vpp_pc")
vcommon = S.Vpp(game+"common.vpp_pc")
cl_ch = load_charlist(vpatch,"charlist_CH")

def dump_vf3(vp, name, n=12):
    e = vp.find(name,"vf3_pc")
    buf = vp.read(e)
    cnt = struct.unpack_from('<I', buf, 8)[0]
    print(f"\n=== {name} count={cnt} ===")
    for k in range(n):
        o = 0xD0 + k*16
        f = struct.unpack_from('<IIII', buf, o)
        # does field match charlist codepoint?
        note=""
        for fi,val in enumerate(f):
            if val in cl_ch: note+=f" f{fi}={val:#x}(={chr(val)})"
        print(f"  glyph {k:4d} rec={f}  {note}")

dump_vf3(vpatch, "fnt_chinese", 14)
dump_vf3(vcommon, "fnt_chinese", 14)
