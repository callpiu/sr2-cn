p = r"F:\sr2-cn\_juice_fix\out4\juiced_CH.cxt"
s = open(p, encoding="utf-8").read()
i = s.find("[MP_SERVER_IP]")
print("=== 末尾原始内容 ===")
print(repr(s[i-60:]))
print()
print("=== 渲染 ===")
for line in s[i-30:].split("\r\n"):
    print("  |%s|" % line)
