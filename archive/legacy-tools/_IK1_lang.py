# -*- coding: utf-8 -*-
# 只读: 语言ID 与 charlist 选择
import re, struct
EXE = r"F:\sr2-cn\_backup_EXE\SR2_pc.exe.before_fontrename"
d = open(EXE, "rb").read()
IB = 0x400000
SECT = [(".text",0x1000,0x9b61f4,0x1000,0x9b7000),
        (".rdata",0x9b8000,0xc7c28,0x9b8000,0xc8000),
        (".data",0xa80000,0x262639c,0xa80000,0x61000)]
def va2off(va):
    for nm,sva,vsz,ro,rsz in SECT:
        if sva<=va<sva+max(vsz,rsz): return ro+(va-sva)
    return None
def cstr(va):
    o=va2off(va)
    if o is None: return "<bad>"
    e=d.find(b"\0",o); return d[o:e].decode("latin1","replace")

print("=== exe 中所有 charlist / JPCharList 字符串 ===")
for m in re.finditer(rb'[ -~]{5,}', d):
    s = m.group()
    if b'harList' in s or b'harlist' in s or s.lower().startswith(b'charlist'):
        print("  off=%#010x  %r" % (m.start(), s))

print("\n=== exe 中 static_/voice_script_ 语言后缀字符串 ===")
for m in re.finditer(rb'[ -~]{4,}', d):
    s = m.group()
    if b'static_' in s or b'voice_script' in s or b'platform_' in s:
        print("  off=%#010x  %r" % (m.start(), s))

print("\n=== 谁写 [0xE8C470] (mov [0xE8C470], r32 = 89 05 70 C4 E8 00) ===")
pat = bytes([0x89,0x05,0x70,0xC4,0xE8,0x00])
for m in re.finditer(re.escape(pat), d):
    print("  @file %#010x" % m.start())
print("  -- 其它形式 mov byte/word --")
for p2,lab in [(bytes([0xC6,0x05,0x70,0xC4,0xE8,0x00]),"byte"),(bytes([0x66,0xC7,0x05,0x70,0xC4,0xE8,0x00]),"word")]:
    for m in re.finditer(re.escape(p2), d):
        print("  %s @file %#010x" % (lab, m.start()))

print("\n=== 谁读 [0xE8C470] (8B 0D 70 C4 E8 00 / A1 70 C4 E8 00) ===")
for p2,lab in [(bytes([0x8B,0x0D,0x70,0xC4,0xE8,0x00]),"mov ecx"),(bytes([0xA1,0x70,0xC4,0xE8,0x00]),"mov eax"),(bytes([0x8B,0x15,0x70,0xC4,0xE8,0x00]),"mov edx")]:
    for m in re.finditer(re.escape(p2), d):
        print("  %s @file %#010x" % (lab, m.start()))
