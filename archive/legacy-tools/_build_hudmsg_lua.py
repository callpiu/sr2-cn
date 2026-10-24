# -*- coding: utf-8 -*-
"""构建 patch.vpp_pc 内 hud_msg 的等长修改版（7817 字节），并做 Lua 语法校验。"""
import sys, os, re, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp
from lupa import LuaRuntime

SRC_VPP = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
ORIG = r"F:/sr2-cn/_lua_vpp/hud_msg.vpp.lua"
OUT = r"F:/sr2-cn/_lua_vpp/hud_msg.mod.lua"
TARGET_SIZE = 7817

def U(s):
    return s.encode("utf-8").decode("latin-1")

raw = open(ORIG, "rb").read()
assert len(raw) == TARGET_SIZE, "原始大小 %d != %d" % (len(raw), TARGET_SIZE)
t = raw.decode("latin-1").replace("\r\n", "\n")

def rep(old, new, cnt=1):
    global t
    assert t.count(old) == cnt, "匹配 %d 次(期望 %d): %r" % (t.count(old), cnt, old[:60])
    t = t.replace(old, new, cnt)

# 0) init 开头加标记（用于确认哪份 lua 在跑）
rep("function hud_msg_init()\n",
    "function hud_msg_init()\n"
    "\tif debug_print ~= nil then debug_print(\"HUDMSG_CN_VPP\\n\") end\n")

# 1) 表 + 匹配函数
rep("Hud_msgs = { }\n",
    "Hud_msgs = { }\n"
    "Hud_msg_cn_pegs = {\n"
    "\t{ \"%s\", \"ui_sub1\" },\n"
    "\t{ \"%s\", \"ui_sub2\" },\n"
    "}\n"
    "function hud_msg_cn_image_for(t)\n"
    "\tif t == nil then return nil end\n"
    "\tfor i = 1, #Hud_msg_cn_pegs do\n"
    "\t\tlocal v = Hud_msg_cn_pegs[i]\n"
    "\t\tif sui_compare_string ~= nil and sui_compare_string(t, v[1]) then\n"
    "\t\t\tif debug_print ~= nil then debug_print(\"HUDMSG_CN_MATCH\\n\") end\n"
    "\t\t\treturn v[2]\n"
    "\t\tend\n"
    "\tend\n"
    "\treturn nil\n"
    "end\n"
    % (U("你的[format][color:green]弟兄们[/format]需要你的保护"),
       U("你的[format][color:green]弟兄们[/format]要出去谈几笔生意，保护他们免遭袭击")))

# 2) init 里 peg_load
rep('\tvint_datagroup_add_subscription("hud_messages", "remove", "hud_msg_remove_message")\nend',
    '\tvint_datagroup_add_subscription("hud_messages", "remove", "hud_msg_remove_message")\n'
    '\tfor i = 1, #Hud_msg_cn_pegs do\n'
    '\t\tif peg_load ~= nil then peg_load(Hud_msg_cn_pegs[i][2]) end\n'
    '\tend\n'
    'end')

# 3) update_region：开 else（bitmap 分支）
rep('\t\t\tif o == 0 then\n'
    '\t\t\t\to = vint_object_create("hud_msg", "text", region.anchor)\n'
    '\t\t\t\tvint_set_property(o, "text_tag", msg.text)\n',
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
    '\t\t\t\t\to = vint_object_create("hud_msg", "bitmap", region.anchor)\n'
    '\t\t\t\t\tvint_set_property(o, "image", im)\n'
    '\t\t\t\t\tvint_set_property(o, "scale", region.text_fmt.scale, region.text_fmt.scale)\n'
    '\t\t\t\t\tvint_set_property(o, "auto_offset", ao)\n'
    '\t\t\t\t\tvint_set_property(o, "horz_align", ha)\n'
    '\t\t\t\t\tmsg.is_image = true\n'
    '\t\t\t\telse\n'
    '\t\t\t\to = vint_object_create("hud_msg", "text", region.anchor)\n'
    '\t\t\t\tvint_set_property(o, "text_tag", msg.text)\n')

# 4) update_region：关 else
rep('\t\t\t\tvint_set_property(o, "line_frame_e", "ui_hud_hlp_bg_e")\n',
    '\t\t\t\tvint_set_property(o, "line_frame_e", "ui_hud_hlp_bg_e")\n'
    '\t\t\t\tend\n')

# 5) h nil 兜底
rep('\t\t\tlocal w, h = vint_get_property(o, "unscaled_size")\n',
    '\t\t\tlocal w, h = vint_get_property(o, "unscaled_size")\n'
    '\t\t\tif h == nil then h = 0 end\n')

# 6) update_message：图片对象不设 text_tag
rep('\t\tif msg.text_obj_h ~= 0 then\n'
    '\t\t\tvint_set_property(msg.text_obj_h, "text_tag", text)\n',
    '\t\tif msg.text_obj_h ~= 0 and not msg.is_image then\n'
    '\t\t\tvint_set_property(msg.text_obj_h, "text_tag", text)\n')

# --- 压缩：去空行、整行注释、行内注释、行首尾空白 ---
lines = t.split("\n")
out = []
for ln in lines:
    s = ln.strip()
    if not s or s.startswith("--"):
        continue
    i = s.find(" --")
    if i >= 0:
        s = s[:i].rstrip()
        if not s:
            continue
    out.append(s)
t = "\n".join(out)
n = len(t.encode("latin-1"))
print("压缩后大小:", n, " 目标:", TARGET_SIZE)
if n > TARGET_SIZE:
    print("★ 超了 %d 字节，需要进一步压缩" % (n - TARGET_SIZE))
else:
    t = t + " " * (TARGET_SIZE - n)
    n2 = len(t.encode("latin-1"))
    assert n2 == TARGET_SIZE, n2
    print("已补齐到", n2)

# --- 语法校验 ---
lua = LuaRuntime(unpack_returned_tuples=True)
try:
    lua.compile(t.encode("latin-1").decode("latin-1"))
    print("Lua 语法校验: OK")
except Exception as e:
    print("Lua 语法错误:", e)
    sys.exit(1)

open(OUT, "wb").write(t.encode("latin-1"))
print("已写出", OUT, "md5=", hashlib.md5(t.encode("latin-1")).hexdigest())
