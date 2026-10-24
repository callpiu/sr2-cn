# -*- coding: utf-8 -*-
"""在 SR2_pc.exe 中搜索语言资源名格式串，确认大小写。"""
import re
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
print("exe size =", len(raw))
for pat in [b'static_%s', b'static_', b'voice_script', b'platform_pc', b'platform_PC',
            b'charlist_%s', b'charlist_', b'.le_strings', b'le_strings',
            b'ForceLanguage', b'Language', b'language']:
    idxs=[m.start() for m in re.finditer(re.escape(pat), raw)]
    print("%-20s 出现 %d 次 %s" % (pat.decode(), len(idxs), [hex(i) for i in idxs[:6]]))
