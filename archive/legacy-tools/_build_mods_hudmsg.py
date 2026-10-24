# -*- coding: utf-8 -*-
"""把中文贴图遮盖逻辑写进 Mods/hud_msg.lua —— 源码保持纯 ASCII（中文用 \\ddd 转义）。"""
import re, sys
from lupa import LuaRuntime

P = r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/hud_msg.lua"

def esc(s):
    return "".join("\\%03d" % b for b in s.encode("utf-8"))

S1 = "你的[format][color:green]弟兄们[/format]需要你的保护"
S2 = "你的[format][color:green]弟兄们[/format]要出去谈几笔生意，保护他们免遭袭击"

t = open(P, "rb").read().decode("utf-8")
assert all(ord(c) < 128 for c in t), "源码里已有非 ASCII 字节"

def rep(old, new, cnt=1):
    global t
    assert t.count(old) == cnt, "匹配 %d 次(期望 %d): %r" % (t.count(old), cnt, old[:50])
    t = t.replace(old, new, cnt)

# 1) 表 + 匹配函数（插在 Hud_msgs = { } 之后）
rep("Hud_msgs = { }\n",
    "Hud_msgs = { }\n"
    "Hud_msg_cn_pegs = {\n"
    "\t{ \"%s\", \"ui_sub1\" },\n"
    "\t{ \"%s\", \"ui_sub2\" },\n"
    "}\n"
    "function hud_msg_cn_image_for(t)\n"
    "\tif t == nil then return nil end\n"
    "\tfor i = 1, 2 do\n"
    "\t\tlocal v = Hud_msg_cn_pegs[i]\n"
    "\t\tif sui_compare_string ~= nil and sui_compare_string(t, v[1]) then\n"
    "\t\t\tif debug_print ~= nil then debug_print(\"HUDMSG_CN_MATCH\\n\") end\n"
    "\t\t\treturn v[2]\n"
    "\t\tend\n"
    "\tend\n"
    "\treturn nil\n"
    "end\n" % (esc(S1), esc(S2)))

# 2) init 里 peg_load
rep('\tvint_datagroup_add_subscription("hud_messages", "remove", "hud_msg_remove_message")\nend',
    '\tvint_datagroup_add_subscription("hud_messages", "remove", "hud_msg_remove_message")\n'
    '\tfor i = 1, 2 do\n'
    '\t\tif peg_load ~= nil then peg_load(Hud_msg_cn_pegs[i][2]) end\n'
    '\tend\n'
    'end')

# 3) update_region：bitmap 分支（失败自动回退 text）
rep('\t\t\t-- create a text item if needed\n'
    '\t\t\tif o == 0 then\n'
    '\t\t\t\to = vint_object_create("hud_msg", "text", region.anchor)\n',
    '\t\t\t-- create a text item if needed\n'
    '\t\t\tif o == 0 then\n'
    '\t\t\t\tlocal im = hud_msg_cn_image_for(msg.text)\n'
    '\t\t\t\tlocal ao, ha\n'
    '\t\t\t\tif region.direction == HUD_MSG_DIR_CENTER then\n'
    '\t\t\t\t\tao = "nw"\n'
    '\t\t\t\t\tha = "center"\n'
    '\t\t\t\telseif region.direction == HUD_MSG_DIR_UP then\n'
    '\t\t\t\t\tao = "sw"\n'
    '\t\t\t\t\tha = "left"\n'
    '\t\t\t\telse\n'
    '\t\t\t\t\tao = "nw"\n'
    '\t\t\t\t\tha = "left"\n'
    '\t\t\t\tend\n'
    '\t\t\t\tif im ~= nil then\n'
    '\t\t\t\t\tlocal b = vint_object_create("hud_msg", "bitmap", region.anchor)\n'
    '\t\t\t\t\tif b ~= nil and b ~= 0 then\n'
    '\t\t\t\t\t\to = b\n'
    '\t\t\t\t\t\tvint_set_property(o, "image", im)\n'
    '\t\t\t\t\t\tvint_set_property(o, "scale", region.text_fmt.scale, region.text_fmt.scale)\n'
    '\t\t\t\t\t\tvint_set_property(o, "auto_offset", ao)\n'
    '\t\t\t\t\t\tvint_set_property(o, "horz_align", ha)\n'
    '\t\t\t\t\t\tmsg.is_image = true\n'
    '\t\t\t\t\tend\n'
    '\t\t\t\tend\n'
    '\t\t\t\tif msg.is_image ~= true then\n'
    '\t\t\t\to = vint_object_create("hud_msg", "text", region.anchor)\n')

# 4) 关掉 if msg.is_image ~= true（放在 line_frame_e 之后）
rep('\t\t\t\tvint_set_property(o, "line_frame_e", "ui_hud_hlp_bg_e")\n',
    '\t\t\t\tvint_set_property(o, "line_frame_e", "ui_hud_hlp_bg_e")\n'
    '\t\t\t\tend\n')

# 5) h nil 兜底
rep('\t\t\tlocal w, h = vint_get_property(o, "unscaled_size")\n',
    '\t\t\tlocal w, h = vint_get_property(o, "unscaled_size")\n'
    '\t\t\tif h == nil then h = 0 end\n')

# 6) 图片对象不设 text_tag
rep('\t\tif msg.text_obj_h ~= 0 then\n'
    '\t\t\tvint_set_property(msg.text_obj_h, "text_tag", text)\n',
    '\t\tif msg.text_obj_h ~= 0 and not msg.is_image then\n'
    '\t\t\tvint_set_property(msg.text_obj_h, "text_tag", text)\n')

assert all(ord(c) < 128 for c in t), "结果含非 ASCII"
open(P, "wb").write(t.encode("utf-8"))
LuaRuntime().compile(t)
print("已写入并语法校验 OK，大小", len(t.encode("utf-8")), " 非ASCII:", sum(1 for c in t if ord(c) > 127))
