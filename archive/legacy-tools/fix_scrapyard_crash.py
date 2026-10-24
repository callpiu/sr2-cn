"""拆车厂崩溃修复 —— 精确移植，只改 2 条记录。

★ 崩溃根因（v417 已定案，2026-10-11 记录）★
引擎用 printf 类格式化器，**按英文原串的占位符【顺序】读参**。
中文译文若把 %ls(宽字符串) 调到 %d/%i(整数) 之前，%ls 会把整数当指针
→ strlen16(0x1) → 崩溃（与现场 EAX=1 吻合）。

★★ 本次只移植这 2 条，其余 v408~v416 的改进一律不引入 ★★
| 记录 | v407（崩溃）                              | v417（修复）                              |
|------|-------------------------------------------|-------------------------------------------|
| A    | ` %ls 清单交付 %d/%d 辆车`  顺序(ls,d,d)  | `交付 %d/%d 辆车 %ls 清单`   顺序(d,d,ls) |
| B    | `数：%i/%i，凭借 %ls 级表现，你获得了$%i`  | `数：%i/%i，你赚到了$%i，凭借 %ls 级表现` |
英文原串对应：
  A: `Delivered %d of %d cars for the %ls list`          → (int,int,str)
  B: `... earned $%i for a %ls level performance`         → (int,int,int,str)

做法：只替换这 2 条记录的 slot 流（长度必须完全相等），其余字节不动。
"""
import sys, os, struct, hashlib, shutil
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC  = os.path.join(GAME, "patch.vpp_pc")
BAK  = SRC + ".beforescrapyardfix.bak"
OUT  = r"F:\sr2-cn\_fix_candidates\patch_scrapyard_fix.vpp_pc"

v = Vpp(SRC)
cl = [int(s) for s in v.read(v.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
S = {i+0x20: cp for i, cp in enumerate(cl)}
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)

def dec(sl): return ''.join(chr(s) if s < 0x100 else (chr(S[s]) if s in S else '<?%d>' % s) for s in sl)
def encode(t):
    out = []
    for ch in t:
        cp = ord(ch)
        if cp < 0x100: out.append(cp)
        else:
            s = c2s.get(ch)
            if s is None: raise ValueError("字表缺字 %r" % ch)
            out.append(s)
    return out

# ---- 目标译文 ----
OLD_A = ' %ls 清单交付 %d/%d 辆车'
NEW_A = '交付 %d/%d 辆车 %ls 清单'
OLD_B = '数：%i/%i，凭借 %ls 级表现，你获得了[format][color:green]$%i[/format]'
NEW_B = '数：%i/%i，你赚到了[format][color:green]$%i[/format]，凭借 %ls 级表现'

print("=== 长度核对 ===")
print("  A: 旧%2d -> 新%2d  %s" % (len(OLD_A), len(NEW_A), "OK" if len(OLD_A)==len(NEW_A) else "★不等"))
print("  B: 旧%2d -> 新%2d  %s" % (len(OLD_B), len(NEW_B), "OK" if len(OLD_B)==len(NEW_B) else "★不等"))
assert len(OLD_A) == len(NEW_A) and len(OLD_B) == len(NEW_B), "长度不等，不能原地替换"

# ---- 定位并替换 ----
e = v.find("static_CH", "le_strings")
b = v.read(e)
bc, count, oa, offs = file_offsets(b)
body = v.data_start + e['body']
seen = set()
done = []
for off in offs:
    sp = body + off + 8
    if sp in seen: continue
    seen.add(sp)
    if not (body < sp <= len(v.data) - 24): continue
    sl = read = []
    i = sp; n = len(v.data)
    while i + 2 <= n:
        x, y = v.data[i], v.data[i+1]
        if x == 0 and y == 0: break
        sl.append((x << 8) | y); i += 2
    if not sl: continue
    txt = dec(sl)
    if txt == OLD_A:
        ns = encode(NEW_A); assert len(ns) == len(sl)
        for j, s in enumerate(ns): struct.pack_into('>H', v.data, sp + j*2, s)
        done.append((sp, OFF_A := 'A', txt, dec(ns)))
    elif txt == OLD_B:
        ns = encode(NEW_B); assert len(ns) == len(sl)
        for j, s in enumerate(ns): struct.pack_into('>H', v.data, sp + j*2, s)
        done.append((sp, 'B', txt, dec(ns)))

print("\n=== 替换结果 ===")
for sp, tag, old, new in done:
    print("  [%s] @0x%X" % (tag, sp))
    print("      旧: %r" % old)
    print("      新: %r" % new)
assert len(done) == 2, "应恰好替换 2 条，实际 %d 条" % len(done)

# ---- 备份与保存 ----
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print("\n✓ 备份原文件 ->", os.path.basename(BAK),
          "md5", hashlib.md5(open(BAK,'rb').read()).hexdigest())
os.makedirs(os.path.dirname(OUT), exist_ok=True)
v.save(OUT)
print("✓ 写出", OUT, "md5", hashlib.md5(open(OUT,'rb').read()).hexdigest())

# ---- 校验 ----
print("\n=== 校验 ===")
a = open(SRC,'rb').read(); b2 = open(OUT,'rb').read()
assert len(a) == len(b2), "大小必须不变"
d = [i for i in range(len(a)) if a[i] != b2[i]]
print("  差异字节数: %d （2条记录各%d槽×2字节）" % (len(d), 18+56))
v2 = Vpp(OUT)
e2 = v2.find("static_CH","le_strings")
bb = v2.read(e2)
bc2,c2,oa2,offs2 = file_offsets(bb)
body2 = v2.data_start + e2['body']; seen2=set(); texts=[]
for off in offs2:
    sp = body2 + off + 8
    if sp in seen2: continue
    seen2.add(sp)
    if not (body2 < sp <= len(v2.data) - 24): continue
    i=sp;n=len(v2.data); sl=[]
    while i+2<=n:
        x,y=v2.data[i],v2.data[i+1]
        if x==0 and y==0: break
        sl.append((x<<8)|y); i+=2
    if sl: texts.append(dec(sl))
print("  新文件含 '交付 %%d/%%d 辆车 %%ls 清单': %s" % any('交付 %d/%d 辆车 %ls 清单' in t for t in texts))
print("  新文件含 '凭借 %%ls 级表现'（前置$%%i）: %s" % any('你赚到了' in t and '%ls 级表现' in t for t in texts))
print("  残留旧顺序 A: %s" % any(OLD_A in t for t in texts))
print("  残留旧顺序 B: %s" % any(OLD_B in t for t in texts))
# 占位符顺序验证
def order(t):
    import re
    return re.findall(r'%l?s|%d|%i|%\d+%s?', t)
for t in texts:
    if '清单交付' in t or '辆 %ls 清单' in t or '级表现' in t:
        print("  顺序: %s -> %s" % (order(t)[:8], t[:50]))
print("\n✓ 构建完成")