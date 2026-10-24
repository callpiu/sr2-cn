import ctypes, ctypes.wintypes as w, subprocess, datetime, sys

out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = None
for line in out.splitlines():
    if line.lower().startswith('"sr2_pc.exe"'):
        pid = int(line.split('","')[1])
        break
print("SR2_pc.exe pid =", pid)
if pid:
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    h = k32.OpenProcess(0x0400, False, pid)   # PROCESS_QUERY_INFORMATION
    if not h:
        print("OpenProcess 失败", ctypes.get_last_error()); sys.exit(1)
    c, e, k, u = (w.FILETIME() for _ in range(4))
    if k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u)):
        ticks = (c.dwHighDateTime << 32) | c.dwLowDateTime
        epoch = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ticks / 10)
        local = epoch + (datetime.datetime.now() - datetime.datetime.utcnow())
        print("进程启动时间 = %s" % local.strftime("%Y-%m-%d %H:%M:%S"))
        print("当前时间     = %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("GetProcessTimes 失败")
    k32.CloseHandle(h)
