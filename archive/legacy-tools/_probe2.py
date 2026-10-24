# -*- coding: utf-8 -*-
"""Runtime memory probe for SR2_pc.exe.
Waits for the game, then scans committed readable memory for:
  SIG_SUB  : static_CH subtitle record (hash F284ED87 + slots)
  SIG_HUD  : static_CH HUD record (hash 5A5AA49A)
  SIG_VF3  : fnt_chinese vf3 U/V array head (U[0],U[1],U[32],U[93],V[93])
  SIG_VF3T : fnt_chinese vf3 U/V array tail
  SIG_BODY : fnt_body_n vf3 record head
  SIG_ATLAS: fnt_chinese atlas DXT3 head
Writes results to F:\\sr2-cn\\_probe_out.txt
"""
import ctypes, ctypes.wintypes as wt, struct, sys, time, os, subprocess
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

OUT = r'F:\sr2-cn\_probe_out.txt'
LOG = open(OUT, 'w', encoding='utf-8')

def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    LOG.write(s + '\n'); LOG.flush()

k32 = ctypes.WinDLL('kernel32', use_last_error=True)

class MBI(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', ctypes.c_uint32), ('__pad', ctypes.c_uint32),
                ('RegionSize', ctypes.c_size_t), ('State', ctypes.c_uint32),
                ('Protect', ctypes.c_uint32), ('Type', ctypes.c_uint32)]

SIG = {
    'SUB':   bytes.fromhex('f284ed870193074c005b0066'),
    'HUD':   bytes.fromhex('5a5aa49a075f0246'),
    'VF3':   struct.pack('<IIIIIII', 1, 32, 63, 94, 1, 1, 1),
    'VF3T':  b'\xff\xff\x00\x00\x1d\x00\x00\x00\x1d\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00',
    'BODY':  b'fnt_body_n.peg',
    'ATLAS': None,
    'U16':   '你的弟兄们需要你的保护'.encode('utf-16-le'),
    'U8':    '你的弟兄们需要你的保护'.encode('utf-8'),
    'CLNAME': b'charlist_ch.txt',
}

def pid_of(name):
    out = subprocess.run(['tasklist', '/fo', 'csv', '/nh'],
                         capture_output=True).stdout.decode('utf-8', 'replace')
    for line in out.splitlines():
        if line.lower().startswith('"%s"' % name.lower()):
            return int(line.split('","')[1])
    return None

def read_atlas_head():
    sys.path.insert(0, r'F:\sr2-cn')
    from _vpp import Vpp
    G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
    pv = Vpp(G + r"\patch.vpp_pc")
    at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
    SIG['ATLAS'] = at[0x4E490:0x4E4B0]
    vf = pv.read(pv.find("fnt_chinese", "vf3_pc"))
    return at, vf

def scan(pid, sigs, maxhits=200):
    h = k32.OpenProcess(0x1F0FFF, False, pid)
    if not h:
        raise OSError('OpenProcess failed: %d' % ctypes.get_last_error())
    addr, hits, total = 0, [], 0
    mbi = MBI()
    pats = [(k, bytes(v)) for k, v in sigs.items() if v]
    while addr < 0x7FFFFFFFFFFF:
        if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        base, size = mbi.BaseAddress or 0, mbi.RegionSize
        prot = mbi.Protect & 0xFF
        if mbi.State == 0x1000 and prot in (0x02, 0x04, 0x06, 0x20, 0x40, 0x80) and 0 < size <= 512*1024*1024:
            buf = ctypes.create_string_buffer(size)
            n = ctypes.c_size_t(0)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(n)) and n.value:
                total += n.value
                d = buf.raw[:n.value]
                for k, pat in pats:
                    st = 0
                    while True:
                        i = d.find(pat, st)
                        if i < 0:
                            break
                        hits.append((k, base + i, d))
                        st = i + 1
                        if len(hits) >= maxhits:
                            break
        addr = base + size
    k32.CloseHandle(h)
    return hits, total

at, vf = read_atlas_head()
log("atlas head sig", SIG['ATLAS'].hex())

log("waiting for SR2_pc.exe ...")
pid = None
for _ in range(900):
    pid = pid_of('SR2_pc.exe')
    if pid:
        break
    time.sleep(1)
if not pid:
    log("GAME NEVER STARTED"); sys.exit(0)
log("game pid", pid, "-- scanning memory (may take 1-3 min) ...")
t0 = time.time()
hits, total = scan(pid, SIG)
log("scanned %.0f MB in %.0f s, hits=%d" % (total/1e6, time.time()-t0, len(hits)))
for k, addr, d in hits[:60]:
    i = addr  # not usable; recompute nothing
    log("  HIT %-6s" % k)

# second pass: for each unique hit region, dump context
log("--- context dump ---")
seen = {}
for k, addr, _ in hits:
    seen.setdefault(k, []).append(addr)
for k, addrs in seen.items():
    log("%s : %d occurrence(s), first 0x%X" % (k, len(addrs), addrs[0]))

log("--- SUB/HUD slot bytes in memory ---")
# re-scan only the two string sigs and print following bytes
h2, _ = scan(pid, {'SUB': SIG['SUB'], 'HUD': SIG['HUD']})
for k, addr, d in h2[:10]:
    i = d.find(SIG[k])
    blob = d[i:i+80]
    log("%s @0x%X hex: %s" % (k, addr, blob.hex(' ')))
    o = 4
    slots = []
    while len(slots) < 40:
        v = struct.unpack_from('>H', blob, o)[0]; o += 2
        if v == 0:
            break
        slots.append(v)
    log("    slots: %s" % slots)
log("DONE")
