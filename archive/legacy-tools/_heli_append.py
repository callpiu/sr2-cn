# -*- coding: utf-8 -*-
"""向 juiced_CH.cxt 末尾追加两条直升机护卫活动提示语（简体 + 绿色高亮格式标签）。CRLF/UTF-8 无 BOM，与原文件一致。"""
import os

D = r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings"
p = os.path.join(D, "juiced_CH.cxt")

raw = open(p, "rb").read()
assert raw.endswith(b"[MP_SERVER_IP]\r\n"), "unexpected tail: " + repr(raw[-30:])
assert "ACT_HELI_PROTECTION_START_MESSAGE" not in raw.decode("utf-8"), "already appended?"

block = (
    "\r\n"
    "[ACT_HELI_PROTECTION_START_MESSAGE]\r\n"
    "\u4f60\u7684[format][color:green]\u5f1f\u5144\u4eec[/format]\u9700\u8981\u4f60\u7684\u4fdd\u62a4\r\n"
    "\r\n"
    "[ACT_HELI_PROTECTION_START_MOVING_MESSAGE]\r\n"
    "\u4f60\u7684[format][color:green]\u5f1f\u5144\u4eec[/format]\u8981\u51fa\u53bb\u8c08\u51e0\u7b14\u751f\u610f\uff0c\u4fdd\u62a4\u4ed6\u4eec\u514d\u906d\u88ad\u51fb\r\n"
).encode("utf-8")

with open(p, "ab") as f:
    f.write(block)

raw2 = open(p, "rb").read()
print("old size", len(raw), "-> new size", len(raw2))
print("---- tail (utf-8) ----")
print(raw2[-260:].decode("utf-8", "replace"))
