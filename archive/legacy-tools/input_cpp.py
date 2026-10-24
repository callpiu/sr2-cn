import os
d = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main"
for fn in ("Input.cpp",):
    p=None
    for root,dirs,fs in os.walk(d):
        if fn in fs: p=os.path.join(root,fn); break
    s=open(p,encoding="utf-8",errors="replace").read()
    lines=s.split("\n")
    print("=== %s (%d 行) ===" % (fn, len(lines)))
    # 打印 340..580 行的关键部分
    for i in range(340, min(600, len(lines))):
        ln = lines[i]
        if any(k in ln for k in ("prompt_image_buffer", "EnableDynamicPrompts", "if (", "return ", "wsprintf", "wcslen", "static", "char ", "getButton", "=> ")):
            print("  %4d: %s" % (i+1, ln.rstrip()[:140]))
