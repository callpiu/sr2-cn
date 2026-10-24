import re, os
p = r"F:\sr2-cn\_juice_fix\out4\juiced_CH.cxt"
b = open(p,"rb").read()
s = b.decode("utf-8")
print("大小 %d 字节, CR=%d LF=%d, 以CRLF结尾=%s" % (len(b), b.count(b"\r"), b.count(b"\n"), b.endswith(b"\r\n")))
ks = re.findall(r'\[([A-Za-z0-9_]+)\]', s)
print("key 数 %d" % len(ks))
print("keys: %s" % " ".join(ks))
print()
for m in re.finditer(r'\[(J_MOUSEFOV|J_FINEAIMONLY|J_FOVMULT)\]\r\n(.*?)\r\n', s, re.S):
    print("  [%s]" % m.group(1))
    print("      %r" % m.group(2))
print()
print("=== 末尾 12 行 ===")
for l in s.split("\r\n")[-14:]:
    print("  |%s|" % l)
