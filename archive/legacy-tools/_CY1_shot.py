import ctypes, ctypes.wintypes as w, subprocess, sys, os
from PIL import Image

u32, u32p = ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)
user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

# 找游戏窗口
out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)

EnumWindows = user32.EnumWindows
CB = ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
found = []
def cb(h, l):
    p = u32()
    user32.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == pid:
        n = ctypes.create_unicode_buffer(512); user32.GetWindowTextW(h, n, 512)
        r = w.RECT(); user32.GetWindowRect(h, ctypes.byref(r))
        vis = user32.IsWindowVisible(h)
        found.append((h, n.value, (r.left, r.top, r.right, r.bottom), bool(vis)))
    return True
EnumWindows(CB(cb), 0)
for h, t, r, v in found:
    print("  hwnd=0x%X title=%r rect=%s visible=%s size=%dx%d" % (h, t, r, v, r[2]-r[0], r[3]-r[1]))

# 截桌面
hdesk = user32.GetDC(0)
W = user32.GetSystemMetrics(0); H = user32.GetSystemMetrics(1)
print("屏幕 %dx%d" % (W, H))
mdc = gdi32.CreateCompatibleDC(hdesk)
bmp = gdi32.CreateCompatibleBitmap(hdesk, W, H)
gdi32.SelectObject(mdc, bmp)
gdi32.BitBlt(mdc, 0, 0, W, H, hdesk, 0, 0, 0x00CC0020)
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", u32), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                ("biPlanes", ctypes.c_ushort), ("biBitCount", ctypes.c_ushort),
                ("biCompression", u32), ("biSizeImage", u32), ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", u32), ("biClrImportant", u32)]
bi = BITMAPINFOHEADER(); bi.biSize = ctypes.sizeof(bi); bi.biWidth = W; bi.biHeight = -H
bi.biPlanes = 1; bi.biBitCount = 32; bi.biCompression = 0
buf = ctypes.create_string_buffer(W * H * 4)
gdi32.GetDIBits(mdc, bmp, 0, H, buf, ctypes.byref(bi), 0)
img = Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB")
outp = r"F:\sr2-cn\_crop\screen_now.png"
img.save(outp)
print("saved", outp, img.size)
ext = img.convert("L").getextrema()
print("亮度范围", ext, "(全黑则游戏为独占全屏)")
