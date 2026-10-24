"""从 patch.vpp_pc/Item_text (XML) 中提取 DRUG_*_DESC 节点的当前中文译文。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME,"patch.vpp_pc"))
for e in v.entries():
    if e['name'].lower()=='item_text':
        ent=e; break
b = v.read(ent)
txt = b.decode('utf-8', errors='replace')

# 找所有形如 <Name>DRUG_..._DESC</Name> 或属性形式
# 先看 DRUG_TWIN_DESC 出现处的上下文
for m in re.finditer(r'DRUG_TWIN_DESC', txt):
    s=max(0,m.start()-120); e2=min(len(txt),m.end()+120)
    print("---- @%d ----" % m.start())
    print(txt[s:e2])
    print()

print("===== 所有 DRUG_*_DESC / *_DESC 键及其邻近文本（粗提取）=====")
# 匹配 <X>...KEY...</X> 形式；也可能是 Key="KEY"
keys = set(re.findall(r'DRUG_[A-Z0-9_]+_DESC', txt))
for k in sorted(keys):
    # 找 key 后面 200 字符里第一个非标签文本
    m = re.search(re.escape(k), txt)
    seg = txt[m.end():m.end()+200]
    # 粗略提取 >文本<
    t = re.search(r'>([^<>]{1,120})<', seg)
    print("  %-28s -> %s" % (k, t.group(1) if t else '(见上下文)'))
