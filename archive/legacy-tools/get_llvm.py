# -*- coding: utf-8 -*-
"""下载 LLVM 工具链（用于交叉编译 x86 DLL）。"""
import os
import sys
import json
import zipfile
import urllib.request
import urllib.parse
import socket

socket.setdefaulttimeout(60)
OUT = r"F:\sr2-cn\_toolchain"
os.makedirs(OUT, exist_ok=True)

PKGS = [
    ("Stride.Dependencies.LLVM.Windows", None),
    ("LLD.Link.Toolsets.win-x64", None),
]


def flat_index(pid):
    low = pid.lower()
    url = "https://api.nuget.org/v3-flatcontainer/%s/index.json" % low
    j = json.loads(urllib.request.urlopen(url).read())
    return j.get("versions", [])


def download(pid, ver, dest):
    low = pid.lower()
    url = "https://api.nuget.org/v3-flatcontainer/%s/%s/%s.%s.nupkg" % (low, ver, low, ver)
    print("  下载 %s" % url)
    fn = os.path.join(dest, "%s.%s.nupkg" % (pid, ver))
    urllib.request.urlretrieve(url, fn)
    print("  -> %s (%d 字节)" % (fn, os.path.getsize(fn)))
    return fn


for pid, _ in PKGS:
    print("=== %s ===" % pid)
    try:
        vs = flat_index(pid)
        print("  可用版本: %s" % vs[-6:])
        if not vs:
            continue
        ver = vs[-1]
        fn = download(pid, ver, OUT)
        # 解压
        ext = os.path.join(OUT, "%s_%s" % (pid, ver))
        os.makedirs(ext, exist_ok=True)
        with zipfile.ZipFile(fn) as z:
            z.extractall(ext)
        print("  解压到 %s" % ext)
        # 列出关键可执行文件
        for root, dirs, fs in os.walk(ext):
            for f in fs:
                if f.lower() in ("clang.exe", "clang-cl.exe", "lld-link.exe", "lld.exe",
                                 "llvm-ar.exe", "clang++.exe", "ld.lld.exe", "wasm-ld.exe"):
                    p = os.path.join(root, f)
                    print("      [可执行] %s  (%d)" % (p.replace(OUT, ".."), os.path.getsize(p)))
    except Exception as e:
        print("  ★ 失败: %s: %s" % (type(e).__name__, e))
    print()
