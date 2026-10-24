#!/usr/bin/env python3
# Scan the whole game directory (and sr2orig backup) for the two activity string hashes.
# Goal: find which file(s) actually contain the activity subtitle text,
# and whether a *different* le_strings holds it (=> that's the real source).

import os, struct

GAME = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
EXTRA = [r"C:/Users/ezplayer/AppData/Local/Temp/sr2orig",
         r"C:/Users/ezplayer/AppData/Local/THQ/Saints Row 2"]

# hash -> candidate byte patterns.
# hash stored as [id1 u16 LE][id2 u16 LE]  => id1,id2 from hash=(id1<<16)|id2
def pats(h):
    id1 = (h >> 16) & 0xFFFF
    id2 = h & 0xFFFF
    a = struct.pack("<HH", id1, id2)        # LE u16, LE u16
    b = struct.pack(">HH", id1, id2)        # BE u16, BE u16
    c = struct.pack("<I", h)                # u32 LE
    d = struct.pack(">I", h)                # u32 BE
    return [a, b, c, d]

HASHES = {
    0x84F287ED: "homies_need_protection (REC1)",
    0x10AF1E62: "homies_heading_out (REC2)",
}
ALLPATS = {}
for h, name in HASHES.items():
    for i, p in enumerate(pats(h)):
        ALLPATS[p] = (h, name, i)

def scan_file(path):
    hits = []
    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception as e:
        return hits
    for p, (h, name, pi) in ALLPATS.items():
        start = 0
        while True:
            idx = data.find(p, start)
            if idx < 0:
                break
            hits.append((h, name, pi, idx))
            start = idx + 1
    return hits

def walk(root):
    for dp, dn, fn in os.walk(root):
        # skip obvious huge media we don't need, but include vpp/cxt/le_strings
        for name in fn:
            low = name.lower()
            if low.endswith((".le_strings", ".vpp_pc", ".cxt", ".g_peg_pc", ".vf3_pc")):
                yield os.path.join(dp, name)

def main():
    roots = [GAME] + EXTRA
    total_files = 0
    found = {}
    for root in roots:
        if not os.path.isdir(root):
            print("SKIP (no dir):", root)
            continue
        for path in walk(root):
            total_files += 1
            h = scan_file(path)
            if h:
                found.setdefault(path, []).extend(h)
    print("Files scanned:", total_files)
    print("="*70)
    if not found:
        print("NO HASH HITS ANYWHERE.")
    else:
        for path, hits in sorted(found.items()):
            rel = os.path.relpath(path, GAME) if path.startswith(GAME) else path
            print(f"\n### {rel}")
            for h, name, pi, off in hits:
                print(f"   hash {h:08X} ({name}) pat#{pi} @ {off} (0x{off:X})")

if __name__ == "__main__":
    main()
