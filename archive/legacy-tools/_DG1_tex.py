import sys, os, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
files = {
 "游戏 textures.vpp_pc": os.path.join(G,"textures.vpp_pc"),
 "原始 textures.vpp_pc": r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig",
}
for tag,p in files.items():
    h=hashlib.md5(open(p,'rb').read(1<<24)).hexdigest()
    print("%-22s %12d  md5(前16MB)=%s" % (tag, os.path.getsize(p), h))
print()
for tag,p in files.items():
    v=Vpp(p)
    for e in v.entries():
        if e['name']=='fnt_chinese':
            b=v.read(e)
            print("%-22s  fnt_chinese ext=%-8s size=%d md5=%s" % (tag, e.get('ext') or '(无)', len(b), hashlib.md5(b).hexdigest()[:12]))
print()
# 官方 charlist 与我的差集
def cl(p):
    v=Vpp(p)
    for e in v.entries():
        if e['name']=='charlist_CH' and e.get('ext')=='txt':
            return [int(s) for s in v.read(e).decode('utf-8','replace').replace('\r','').split('\n') if s.strip().isdigit()]
    return None
off = cl(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
cur = cl(os.path.join(G,"patch.vpp_pc"))
print("官方 charlist %d 条, 当前 %d 条" % (len(off), len(cur)))
so, sc = set(off), set(cur)
print("官方有而当前缺: %d 个 -> %s" % (len(so-sc), [hex(x) for x in sorted(so-sc)][:50]))
print("当前有而官方无: %d 个 -> %s" % (len(sc-so), [hex(x) for x in sorted(sc-so)][:20]))
