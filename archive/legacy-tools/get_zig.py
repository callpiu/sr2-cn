# -*- coding: utf-8 -*-
"""下载 zig 工具链（自带 C/C++ 编译器 + 链接器，能生成合法 PE32）。"""
import os
import json
import zipfile
import urllib.request
import socket

socket.setdefaulttimeout(120)
OUT = r"F:\sr2-cn\_toolchain\zig"
os.makedirs(OUT, exist_ok=True)

PKGS = ["Vezel.Zig.Sdk", "Vezel.Zig.Toolsets.win-x64"]


def versions(pid):
    u = "https://api.nuget.org/v3-flatcontainer/%s/index.json" % pid.lower()
    return json.loads(urllib.request.urlopen(u).read()).get("versions", [])


for pid in PKGS:
    print("=== %s ===" % pid)
    try:
        vs = versions(pid)
        print("  版本: %s" % vs[-5:])
        if not vs:
            continue
        ver = vs[-1]
        url = ("https://api.nuget.org/v3-flatcontainer/%s/%s/%s.%s.nupkg"
               % (pid.lower(), ver, pid.lower(), ver))
        fn = os.path.join(OUT, "%s.%s.nupkg" % (pid, ver))
        print("  下载 %s" % url)
        urllib.request.urlretrieve(url, fn)
        print("  -> %d 字节" % os.path.getsize(fn))
        ext = os.path.join(OUT, "%s_%s" % (pid, ver))
        os.makedirs(ext, exist_ok=True)
        with zipfile.ZipFile(fn) as z:
            z.extractall(ext)
        print("  解压到 %s" % ext)
        for root, dirs, fs in os.walk(ext):
            for f in fs:
                if f.lower() in ("zig.exe", "zig.cmd", "zig"):
                    p = os.path.join(root, f)
                    print("      [可执行] %s (%d)" % (p, os.path.getsize(p)))
    except Exception as e:
        print("  ★ 失败: %s: %s" % (type(e).__name__, e))
    print()
