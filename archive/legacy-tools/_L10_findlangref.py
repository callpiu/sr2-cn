# -*- coding: utf-8 -*-
"""在 exe 中定位引用语言串地址(如 0xE25FF8='US')的代码，确定真语言表。"""
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000
def find_ptr_refs(fileoff_ptr):
    """找 .text 中立即数等于该 VA 的位置 (mov reg, imm32)"""
    va = fileoff_ptr + BASE
    b = va.to_bytes(4,'little')
    import re
    res=[]
    for m in re.finditer(re.escape(b), raw[0:0x9B8000]):
        res.append(m.start())
    return res, va

for name, fo in [('US',0xA25FF8), ('CH',0x9D69EC), ('RU',0xA25FDC), ('CZ',0xA25FE4)]:
    refs, va = find_ptr_refs(fo)
    print("%s VA=0x%08X  被立即数引用 %d 次: %s" % (name, va, len(refs), [hex(r) for r in refs[:10]]))
    # 查这些位置附近的相对引用（lea）通常在 .text
    print()
