# -*- coding: utf-8 -*-
"""关键：定位活动字幕的真实来源。
活动字幕 = voice_script?  还是 hud.lua 里的硬编码? 还是 static?
检查 hud.lua / dialog_box.lua 里的中文字符串编码方式。
"""
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
import os
for fn in ['hud.lua','dialog_box.lua','activity_level.lua']:
    p=os.path.join(G,'Mods',fn)
    if not os.path.exists(p):
        p=os.path.join(G,'Mods','JUICED - Lua Libraries',fn)
    if not os.path.exists(p):
        print(fn,"未找到"); continue
    raw=open(p,'rb').read()
    print("=== %s (%d bytes) ===" % (fn, len(raw)))
    # 找中文 (UTF-8 三字节 E4-E9)
    import re
    # 统计 UTF-8 中文
    m=re.findall(rb'[\xe4-\xe9][\x80-\xbf]{2}', raw)
    print("  UTF-8 中文字节组数 =", len(m))
    if m:
        s=raw.decode('utf-8','replace')
        # 找含"弟兄"的上下文
        for kw in ['弟兄','保护','直升机','字幕']:
            i=s.find(kw)
            if i>=0:
                print("  含'%s' @%d: ...%s..." % (kw,i,s[max(0,i-40):i+40].replace('\n','\\n')))
    # 找 GBK 中文
    mg=re.findall(rb'[\xb0-\xf7][\xa1-\xfe]', raw)
    print("  GBK 中文字节组数 =", len(mg))
    print()
