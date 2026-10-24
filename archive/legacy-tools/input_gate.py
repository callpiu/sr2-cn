import os
d = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main"
for fn in ("Input.cpp",):
    p=None
    for root,dirs,fs in os.walk(d):
        if fn in fs: p=os.path.join(root,fn); break
    s=open(p,encoding="utf-8",errors="replace").read()
    lines=s.split("\n")
    print("=== 关键函数定义与 EnableDynamicPrompts 的关联 ===")
    for i,ln in enumerate(lines):
        if ("EnableDynamicPrompts" in ln) or ("prompt_image_buffer" in ln and "wchar_t" in ln) or \
           ln.strip().startswith("bool ") or ln.strip().startswith("wchar_t* ") or \
           ("__declspec" in ln) or ln.strip().startswith("namespace"):
            print("  %4d: %s" % (i+1, ln.rstrip()[:135]))
    print()
    print("=== 155..175 行（EnableDynamicPrompts 的门控）===")
    for i in range(154, min(180, len(lines))):
        print("  %4d: %s" % (i+1, lines[i].rstrip()[:135]))
