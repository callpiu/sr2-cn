"""FQ3: find every vint_proj in every VPP, and show the font alias table in each.
"""
import sys, os, re, glob, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

hits = []
for p in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(p)
    except Exception as ex:
        continue
    for e in v.entries():
        if e["ext"] == "vint_proj":
            hits.append((p, e))

print("vint_proj entries found:", len(hits))
for p, e in hits:
    v = Vpp(p)
    raw = v.read(e)
    txt = raw.decode("utf-8", "replace")
    print("=" * 70)
    print("%s :: %s.%s  size=%d  md5=%s" % (
        os.path.basename(p), e["name"], e["ext"], len(raw), hashlib.md5(raw).hexdigest()))
    for m in re.finditer(r"<font_info>(.*?)</font_info>", txt, re.S):
        blk = m.group(1)
        fn = re.search(r"<filename>(.*?)</filename>", blk)
        al = re.search(r"<alias>(.*?)</alias>", blk)
        fo = re.search(r"<filename_overlay>(.*?)</filename_overlay>", blk)
        print("   alias=%-20s filename=%-18s overlay=%s" % (
            al.group(1) if al else "?", fn.group(1) if fn else "?", fo.group(1) if fo else "?"))

print()
print("== loose vint_proj on disk ==")
for root, dirs, files in os.walk(G):
    for f in files:
        if "vint_proj" in f.lower():
            fp = os.path.join(root, f)
            print("   %s (%d)" % (os.path.relpath(fp, G), os.path.getsize(fp)))
