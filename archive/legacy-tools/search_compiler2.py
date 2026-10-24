# -*- coding: utf-8 -*-
"""在 NuGet 上找可用于构建 x86 DLL 的 C++ 编译器。"""
import urllib.request
import urllib.parse
import json
import socket

socket.setdefaulttimeout(20)


def s(q, take=15):
    url = ("https://azuresearch-usnc.nuget.org/query?q=%s&take=%d"
           % (urllib.parse.quote(q), take))
    try:
        j = json.loads(urllib.request.urlopen(url).read())
        return j.get("data", [])
    except Exception as e:
        return [{"id": "ERR", "version": "%s: %s" % (type(e).__name__, e)}]


for q in ("w64devkit", "llvm-mingw", "zig", "libtcc", "chibicc",
          "MinGW-w64 toolchain", "gcc toolchain windows", "clang toolchain",
          "cc65", "msvc build tools x86"):
    print("=== %s ===" % q)
    for d in s(q):
        print("  %-48s %-16s dl=%-9s %s" % (
            d.get("id", "?"), d.get("version", "?"), d.get("totalDownloads", 0),
            (d.get("description") or "").replace("\n", " ")[:60]))
    print()
