# -*- coding: utf-8 -*-
"""检查能否联网下载编译器（MSVC Build Tools / MinGW）。"""
import urllib.request
import socket

socket.setdefaulttimeout(8)
for u in ("https://api.nuget.org/v3/index.json",
          "https://www.nuget.org",
          "https://github.com",
          "https://aka.ms",
          "https://download.visualstudio.microsoft.com"):
    try:
        r = urllib.request.urlopen(u)
        print("  [可达] %-50s -> %d" % (u, r.status))
    except Exception as e:
        print("  [不可达] %-48s -> %s" % (u, type(e).__name__))
