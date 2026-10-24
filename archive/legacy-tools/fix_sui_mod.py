import hashlib

P = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/dialog_box.lua'
raw = open(P, 'rb').read()
bak = open(P + '.sui.bak', 'rb').read()
assert raw == bak, 'file already modified unexpectedly'

i = raw.find(b'SUI_LAN_COOP_SP')
assert i > 0
# 从注释行"-- Show "Single Player"" 开始整块替换
anchor = b'\t-- Show "Single Player" for "Waiting for Player" dialog (experimental) [nclok1405]'
ls = raw.find(anchor)
assert ls > 0, 'anchor not found'
assert raw.find(anchor, ls + 1) == -1, 'anchor not unique'
# 找到该块结尾的 "\n\tend"
end_marker = b'\t\toption_2 = "LEADERBOARDS_SP"\n\tend'
ej = raw.find(end_marker, ls)
assert ej > 0, 'end marker not found'
ej_end = ej + len(end_marker)

old_block = raw[ls:ej_end]
print('--- OLD BLOCK ---')
print(old_block.decode('utf-8'))
assert b'SUI_LAN_COOP_SP' in old_block
assert b'LEADERBOARDS_SP' in old_block

new_block = (
    b'\t-- Show "Single Player" for "Waiting for Player" dialog (experimental) [nclok1405]\n'
    b'\t-- 2026-10-18 ZH fix: Juice used a fabricated tag -- SUI_LAN / COOP_SP --\n'
    b'\t-- that exists in NO language table, so the raw tag leaked onto the screen.\n'
    b'\t-- Use the real official tag MENU_TITLE_NOTICE instead, properly localized.\n'
    b'\tif sui_compare_string(body, "MULTI_COOP_WAITING_PLAYER_2") and (option_2 == nil) then\n'
    b'\t\theader = body\n'
    b'\t\tbody = "MENU_TITLE_NOTICE"\n'
    b'\t\toption_2 = "CONTROL_CANCEL"\n'
    b'\tend'
)

out = raw[:ls] + new_block + raw[ej_end:]
assert b'body = "SUI_LAN_COOP_SP"' not in out, 'tag still present'
assert b'"MENU_TITLE_NOTICE"' in out
assert out.count(b'MULTI_COOP_WAITING_PLAYER_2') == raw.count(b'MULTI_COOP_WAITING_PLAYER_2')

# 只比较代码行（剔除新增注释行），确保逻辑行数不变
new_code = b'\n'.join(l for l in new_block.split(b'\n') if not l.strip().startswith(b'--'))
old_code = b'\n'.join(l for l in old_block.split(b'\n') if not l.strip().startswith(b'--'))
assert new_code.count(b'\n') == old_code.count(b'\n'), (new_code, old_code)
# 换行风格：原文全部 LF（CRLF 计数为 0），保持不变
assert raw.count(b'\r') == 0, 'unexpected CR in original'
assert out.count(b'\r') == 0

open(P, 'wb').write(out)
print()
print('--- NEW BLOCK ---')
print(new_block.decode('utf-8'))
print()
print('old size', len(raw), '-> new size', len(out))
print('new md5', hashlib.md5(out).hexdigest())