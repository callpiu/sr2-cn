# -*- coding: utf-8 -*-
import re, struct
EXE = r"F:\sr2-cn\_backup_EXE\SR2_pc.exe.before_fontrename"
d = open(EXE, "rb").read()
IB = 0x400000

def dump(o0, o1):
    print("=== file %#x .. %#x ===" % (o0, o1))
    o = o0
    while o < o1:
        row = d[o:o+16]
        print("%08x  %-47s  %s" % (o, " ".join("%02X"%b for b in row),
              "".join(chr(b) if 32<=b<127 else "." for b in row)))
        o += 16

dump(0xA26000, 0xA260C0)

print("\n=== 谁引用 charlist_%%s.txt (VA %#x) ===" % (IB+0xA26070))
for m in re.finditer(re.escape(struct.pack("<I", IB+0xA26070)), d):
    print("  @file %#010x" % m.start())
print("=== 谁引用 static_%%s.le_strings (VA %#x) ===" % (IB+0xA26024))
for m in re.finditer(re.escape(struct.pack("<I", IB+0xA26024)), d):
    print("  @file %#010x" % m.start())
print("=== 谁引用 platform_%%s (VA %#x) ===" % (IB+0xA26098))
for m in re.finditer(re.escape(struct.pack("<I", IB+0xA26098)), d):
    print("  @file %#010x" % m.start())

print("\n=== 写 [0xE8C470] 的其它指令形式 ===")
for p,lab in [(bytes([0xA3,0x70,0xC4,0xE8,0x00]),"mov [mem],eax"),
              (bytes([0x89,0x15,0x70,0xC4,0xE8,0x00]),"mov [mem],edx"),
              (bytes([0x89,0x0D,0x70,0xC4,0xE8,0x00]),"mov [mem],ecx")]:
    for m in re.finditer(re.escape(p), d):
        print("  %s @file %#010x" % (lab, m.start()))

print("\n=== 附近 .rdata 里的语言后缀候选 (3字母大写) ===")
for m in re.finditer(rb'\b(CH|US|UK|FR|DE|ES|IT|NL|CZ|PL|RU|JP|KR|SE|DK|BR|MX|CN|TW)\x00', d[0xA25000:0xA27000]):
    print("  @%#x  %r" % (0xA25000+m.start(), m.group()[:-1]))
