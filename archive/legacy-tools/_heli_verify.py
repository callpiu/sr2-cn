# -*- coding: utf-8 -*-
import os
D = r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings"
p = os.path.join(D, "juiced_CH.cxt")
raw = open(p, "rb").read()
txt = raw.decode("utf-8")  # raises if broken
lines = txt.split("\r\n")
print("total lines:", len(lines))
print("CRLF pairs == LF count ?", raw.count(b"\r\n") == raw.count(b"\n"))
for tid in ["ACT_HELI_PROTECTION_START_MESSAGE", "ACT_HELI_PROTECTION_START_MOVING_MESSAGE"]:
    print(tid, "count =", txt.count("[" + tid + "]"))
# print the two new entries cleanly
i = txt.find("[ACT_HELI_PROTECTION_START_MESSAGE]")
print("---- new block ----")
print(txt[i:].strip())
print("decodes fully as UTF-8: OK")
