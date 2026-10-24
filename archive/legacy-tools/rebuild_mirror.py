"""Rebuild static_CH / voice_script_CH to mirror the OFFICIAL US table structure.

Strategy (guaranteed correct because US ships & works in-game):
  * keep US bucket count (static=1024, voice=512)
  * place every hash in the EXACT bucket + in-bucket order US used
  * keep CH text for each hash (raw slot bytes), fall back to US text if absent
  * id bytes copied verbatim from US (so the lookup hash is unchanged)

Format (verified empirically):
  header: magic u32 | ver u16 | buckets u16 | count u32   (12 bytes)
  bucket table: buckets * (count u32, addr u32)           (8 bytes each)
      addr = absolute file offset of this bucket's FIRST pointer
  pointer array: count * u32  (absolute file offsets to records)
  record: [id1 LE u16][id2 LE u16][UTF-16BE units...][0x0000]
"""
import struct, sys, os, shutil
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
MAGIC = 0xA84C7F73

def parse(name):
    e = vpp.find(name, 'le_strings')
    d = vpp.read(e)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    assert magic == MAGIC, (name, hex(magic))
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    buckets_info = [struct.unpack_from('<II', d, 12 + b*8) for b in range(buckets)]
    loc_bucket = {}
    for b in range(buckets):
        bc, ba = buckets_info[b]
        for k in range(bc):
            loc_bucket[ba + k*4] = b
    # per-bucket ordered (hash, id_bytes, text_bytes)
    us_order = {b: [] for b in range(buckets)}
    for k, off in enumerate(ptrs):
        b = loc_bucket[off_at + k*4]
        id_bytes = d[off:off+4]
        id1, id2 = struct.unpack_from('<HH', id_bytes)
        h = (id1 << 16) | id2
        # text units (no terminator)
        i = off+4
        while i+2 <= len(d):
            v = struct.unpack_from('>H', d, i)[0]
            if v == 0:
                break
            i += 2
        text = d[off+4:i]
        us_order[b].append((h, id_bytes, text))
    return d, us_order, buckets, count

def ch_text_map(name):
    e = vpp.find(name, 'le_strings')
    d = vpp.read(e)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    m = {}
    for off in ptrs:
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1 << 16) | id2
        i = off+4
        while i+2 <= len(d):
            v = struct.unpack_from('>H', d, i)[0]
            if v == 0:
                break
            i += 2
        if h in m:   # dup -> keep first
            continue
        m[h] = d[off+4:i]
    return m

def rebuild(us_name, ch_name):
    dU, us_order, nb, count = parse(us_name)
    ch_map = ch_text_map(ch_name)
    # build new blob
    # layout: header(12) + bucket table(nb*8) + pointer array(count*4) + records
    # We'll first lay out records in bucket order, recording offsets.
    records = []            # list of (id_bytes, text_bytes) in write order
    bucket_count = []
    bucket_start_idx = []
    gi = 0
    for b in range(nb):
        items = us_order[b]
        bucket_count.append(len(items))
        bucket_start_idx.append(gi)
        for (h, id_bytes, us_text) in items:
            txt = ch_map.get(h, us_text)   # CH text if present else US text
            records.append((id_bytes, txt))
            gi += 1
    assert gi == count, (gi, count)
    # assemble: pre-allocate header + bucket table + pointer array region,
    # then write records after it.
    ptr_array_off = 12 + nb*8
    rec_region_start = ptr_array_off + count*4
    out = bytearray(rec_region_start)          # header+bucketT+ptrArray reserved (zeros)
    struct.pack_into('<IHHI', out, 0, MAGIC, 1, nb, count)
    p = rec_region_start
    ptrs_out = []
    for (id_bytes, txt) in records:
        rec = id_bytes + txt + b'\x00\x00'
        ptrs_out.append(p)
        out += rec
        p += len(rec)
    # now backfill pointer array (in same order as records)
    for idx, off in enumerate(ptrs_out):
        struct.pack_into('<I', out, ptr_array_off + idx*4, off)
    # bucket table: addr = absolute offset of first pointer of bucket
    for b in range(nb):
        if bucket_count[b] == 0:
            addr = ptr_array_off + bucket_start_idx[b]*4   # still point somewhere valid
        else:
            addr = ptr_array_off + bucket_start_idx[b]*4
        struct.pack_into('<II', out, 12 + b*8, bucket_count[b], addr)
    return bytes(out), nb, count, ch_map

def verify_blob(name, blob, us_name):
    d = blob
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    buckets_info = [struct.unpack_from('<II', d, 12 + b*8) for b in range(buckets)]
    loc_bucket = {}
    for b in range(buckets):
        bc, ba = buckets_info[b]
        for k in range(bc):
            loc_bucket[ba + k*4] = b
    hashes = {}
    used = set()
    for k, off in enumerate(ptrs):
        b = loc_bucket.get(off_at + k*4, -1)
        used.add(b)
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        hashes[h] = off
        # bounds check
        assert 0 < off <= len(d)-6
    used.discard(-1)
    # compare hashes vs US
    dU, us_order, nbU, cU = parse(us_name)
    us_hashes = set()
    for b in us_order:
        for (h,_,_) in us_order[b]:
            us_hashes.add(h)
    missing = us_hashes - set(hashes)
    extra = set(hashes) - us_hashes
    print(f"  VERIFY {name}: nb={buckets} count={count} buckets_used={len(used)}/{buckets} "
          f"missing_vs_US={len(missing)} extra_vs_US={len(extra)}")
    return missing, extra

if __name__ == '__main__':
    vpp = Vpp(P)
    stage = r'F:\sr2-cn\_rebuilt'
    os.makedirs(stage, exist_ok=True)
    for us_n, ch_n in [('static_US', 'static_CH'), ('voice_script_US', 'voice_script_CH')]:
        new_blob, nb2, count, ch_map = rebuild(us_n, ch_n)
        outf = os.path.join(stage, ch_n + '.le_strings')
        open(outf, 'wb').write(new_blob)
        print(f"\n{ch_n}: rebuilt nb={nb2} count={count} blob_size={len(new_blob)} "
              f"CH hashes available={len(ch_map)} -> {outf}")
        verify_blob(ch_n, new_blob, us_n)
    print("\nStaged rebuilds written. Verify before deploying.")
