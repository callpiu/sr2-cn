# -*- coding: utf-8 -*-
"""在 NuGet 上找 llvm-dlltool / mingw 导入库 / 任何含 .lib 的包。"""
import urllib.request
import urllib.parse
import json
import socket

socket.setdefaulttimeout(20)


def s(q, take=20):
    url = ("https://azuresearch-usnc.nuget.org/query?q=%s&take=%d"
           % (urllib.parse.quote(q), take))
    try:
        j = json.loads(urllib.request.urlopen(url).read())
        return j.get("data", [])
    except Exception as e:
        return [{"id": "ERR:" + str(e), "version": ""}]


for q in ("llvm tools windows", "llvm binary", "clang llvm windows binaries",
          "dlltool", "mingw runtime", "windows sdk lib", "win32 lib import"):
    print("=== %s ===" % q)
    for d in s(q):
        print("  %-52s %-14s dl=%s" % (d.get("id", "?"), d.get("version", ""),
                                       d.get("totalDownloads", 0)))
    print()
