# -*- coding: utf-8 -*-
"""在 NuGet 上搜索可用的 Windows C/C++ 编译器包。

（github.com 不可达，但 nuget.org / aka.ms 可达）
"""
import urllib.request
import json
import socket

socket.setdefaulttimeout(15)

QUERIES = [
    "mingw",
    "mingw-w64",
    "clang",
    "llvm",
    "MSVC",
    "msvc-toolset",
    "windows-sdk",
    "gcc",
    "tcc",
    "tinycc",
]


def search(q, take=12):
    url = ("https://azuresearch-usnc.nuget.org/query?q=%s&take=%d&prerelease=false"
           % (urllib.parse.quote(q), take))
    try:
        r = urllib.request.urlopen(url)
        j = json.loads(r.read())
        return j.get("data", [])
    except Exception as e:
        return [{"__err": "%s: %s" % (type(e).__name__, e)}]


import urllib.parse

for q in QUERIES:
    print("=== 搜索 '%s' ===" % q)
    for d in search(q):
        if "__err" in d:
            print("  ★ %s" % d["__err"])
            continue
        pid = d.get("id", "?")
        ver = d.get("version", "?")
        desc = (d.get("description") or "").replace("\n", " ")[:90]
        dl = d.get("totalDownloads", 0)
        print("  %-44s %-16s dl=%-9d %s" % (pid, ver, dl, desc))
    print()
