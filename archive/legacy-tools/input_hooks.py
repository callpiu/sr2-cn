import os
d = r"F:\sr2-cn\juicedsrc\Saints-Row-2-Juiced-Patch-main"
p=None
for root,dirs,fs in os.walk(d):
    if "Input.cpp" in fs: p=os.path.join(root,"Input.cpp"); break
lines=open(p,encoding="utf-8",errors="replace").read().split("\n")
print("=== 钩子安装处（搜索 create_inline / create_mid 与这两个钩子）===")
for i,ln in enumerate(lines):
    if ("getpckeyboardimage" in ln or "pc_get_action_pad_pure_text" in ln) and ("Hook" in ln or "create_" in ln or "apply" in ln):
        print("  %4d: %s" % (i+1, ln.rstrip()[:140]))
print()
print("=== 1045..1070 行（EnableDynamicPrompts 的门控）===")
for i in range(1044, min(1075, len(lines))):
    print("  %4d: %s" % (i+1, lines[i].rstrip()[:135]))
print()
print("=== 590..615 行（pc_get_action_pad_pure_text_hook）===")
for i in range(589, min(616, len(lines))):
    print("  %4d: %s" % (i+1, lines[i].rstrip()[:135]))
