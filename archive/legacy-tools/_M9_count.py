# -*- coding: utf-8 -*-
"""决定性：loadcharlist@0x7F4582 用 "count=%u" 解析文件头。
检查 charlist_CH.txt 是否有 count= 行，与其它语言表对比。
"""
import sys, re
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
print("exe 中 'count=%u' 位于 0xE26080 (VA), 即 loadcharlist 解析文件头用\n")
for nm in ['charlist_CH','charlist_JP','charlist_CZ','charlist_SK','charlist_PL','charlist_RU','JPCharList']:
    raw=v.read(v.find(nm,'txt'))
    first = raw.split(b'\n')[0][:80]
    has_count = b'count=' in raw[:200]
    print("=== %s ===" % nm)
    print("  第一个 \\n 前的内容: %r" % first)
    print("  前 200 字节含 'count=' ?", has_count)
    # 找 count=NNN
    m=re.search(rb'count=(\d+)', raw[:300])
    if m: print("  count=%s" % m.group(1).decode())
    print()
