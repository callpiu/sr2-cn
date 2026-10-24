import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
def cl(p):
    v=Vpp(p); t=v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
nums = cl(os.path.join(G,"patch.vpp_pc"))
SENT = "你的弟兄们需要你的保护"
codes = [nums.index(ord(c))+32 for c in SENT]
print("句子:", SENT)
print("期望压缩码:", codes, [hex(c) for c in codes])
pat = b"".join(struct.pack('<H', c) for c in codes)
print("字节模式:", pat.hex())
targets = {
 "当前 patch.vpp_pc": os.path.join(G,"patch.vpp_pc"),
 "原始 patch.vpp_pc": r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig",
}
for tag,p in targets.items():
    v=Vpp(p)
    for e in v.entries():
        if 'strings' in e.get('ext','') or e['name'].startswith('static') or 'le_strings' in e.get('ext',''):
            b=v.read(e)
            k=b.find(pat)
            if k>=0: print("  [命中] %s / %s.%s  偏移=%d" % (tag, e['name'], e.get('ext',''), k))
print("--- 也搜原始版(应编码自官方字符表, 找不到属正常) ---")
