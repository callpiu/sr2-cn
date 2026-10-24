#!/usr/bin/env python3
# Remove the literal ASCII "[format][color:green]...[/format]" tags from the two
# activity records (84F287ED, 10AF1E62) in static_CH, restoring the original
# Chinese text and padding with spaces to preserve record byte-length (so all
# le_strings internal pointers stay valid). Hypothesis: the activity/co-op HUD
# cannot parse the ASCII format tags and desyncs its glyph decode -> garble.
import sr2lib, struct, shutil, os, datetime

GAME = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
SRC  = GAME + r"/patch.vpp_pc"
BAK  = SRC + f".v533_tagfix_{datetime.datetime.now():%Y%m%d_%H%M%S}.bak"

v = sr2lib.Vpp(SRC)
ents = {(e['name']+e.get('ext','')).lower():e for e in v.entries()}
cl = v.read(ents['charlist_chtxt'])
codepoints=[]
for x in cl.decode('utf-8').split():
    if x.strip().isdigit(): codepoints.append(int(x))
cp2idx={cp:i for i,cp in enumerate(codepoints)}

def encode(text):
    out=bytearray()
    for ch in text:
        if ch==' ':
            idx=0
        else:
            cp=ord(ch)
            if cp not in cp2idx:
                raise SystemExit(f"char {ch!r} not in charlist_CH")
            idx=cp2idx[cp]
        out += struct.pack(">H", idx+0x20)
    return bytes(out)

def parse_recs(data):
    ver,buckets,count=struct.unpack_from("<HHI",data,4)
    off=12
    for i in range(buckets): off+=8
    ptrs=[]
    for i in range(count):
        ptrs.append(struct.unpack_from("<I",data,off)[0]); off+=4
    recs=[]
    for p in ptrs:
        id1,id2=struct.unpack_from("<HH",data,p)
        q=p+4; slots=[]; term=q
        while q+2<=len(data):
            w=struct.unpack_from(">H",data,q)[0]
            if w==0: term=q+2; break
            slots.append(w); q+=2
        recs.append(dict(p=p,id1=id1,id2=id2,slot_start=p+4,term=term,slots=slots))
    return recs

blob=v.read(ents['static_chle_strings'])
recs=parse_recs(blob)

targets={
    0x84F287ED:"你的弟兄们需要你的保护",
    0x10AF1E62:"你的弟兄们要出去谈几笔生意，保护他们免遭袭击",
}

# work on a mutable bytearray copy of the blob
b=bytearray(blob)
for r in recs:
    h=(r['id1']<<16)|r['id2']
    if h in targets:
        new_text=targets[h]
        new_slots=encode(new_text)
        old_len=r['term']-r['slot_start']   # includes the 0x0000 terminator
        # pad with space slots (0x0020) to preserve length
        pad_needed=old_len-len(new_slots)-2  # -2 for terminator we add
        if pad_needed<0:
            raise SystemExit(f"record {h:08X} would grow ({old_len} vs {len(new_slots)+2})")
        payload=new_slots+b'\x00\x20'* (pad_needed//2) + b'\x00\x00'
        # ensure exact length
        payload=bytearray(payload)
        if len(payload)<old_len:
            payload+=b'\x00\x20'*((old_len-len(payload))//2)
        payload=payload[:old_len]
        assert len(payload)==old_len, (len(payload),old_len)
        b[r['slot_start']:r['term']]=payload
        print(f"patched {h:08X}: '{new_text}' (orig slots {old_len//2-1} -> new content {len(new_slots)//2} chars + spaces)")

# verify by re-parsing
recs2=parse_recs(bytes(b))
def dec(slots):
    out=[]
    for w in slots:
        if w<0x20: out.append(f"<{w:02X}>")
        else:
            i=w-0x20
            out.append(chr(codepoints[i]) if 0<=i<len(codepoints) else f"[{w}]")
    return "".join(out)
print("verify:")
for r in recs2:
    h=(r['id1']<<16)|r['id2']
    if h in targets:
        print(f"  {h:08X}: {dec(r['slots'])}")

# backup then write
shutil.copy2(SRC, BAK)
print("backup ->", BAK)
v.replace_body_appended(ents['static_chle_strings'], bytes(b))
v.save(SRC)
print("written ->", SRC)
print("new md5:", __import__('hashlib').md5(open(SRC,'rb').read()).hexdigest())
