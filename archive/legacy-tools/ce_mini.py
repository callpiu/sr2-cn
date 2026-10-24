# -*- coding: utf-8 -*-
"""
迷你 Cheat Engine —— 专用于「SR2 直升机突击活动字幕乱码」排查

纯 ctypes 调用 Windows API，无需安装 Cheat Engine，无需手动点任何按钮。
自动完成：找进程 -> 提权 -> 遍历内存区 -> 搜索字节模式 -> 定位 -> 解码上下文

用法
    1) 启动《黑道圣徒2》（★ 不需要在字幕出现的那一瞬间扫，见下）
    2) 运行：
         python ce_mini.py scan          # 全套扫描（默认）
         python ce_mini.py wait          # 先等游戏出现再自动扫（可以先开脚本再慢慢进游戏）
         python ce_mini.py ps            # 只看进程列表
         python ce_mini.py dump ADDR     # 查看某个地址周围的字节并解码
    3) 输出会自动存到 F:/sr2-cn/_扫描结果/scan_YYYYMMDD_HHMMSS.txt，把文件发我就行

★ 时机不用抢（重要）
    le_strings 字符串表是【整表一次性加载常驻内存】的：游戏一进主菜单，
    12250 条中文记录就全在内存里了，跟字幕此刻有没有显示在屏幕上【完全无关】。
    所以：什么时候扫都行，扫 10~40 秒期间游戏可以继续跑，字幕错过一百次也不影响结果。

搜索原理（为什么这样搜）
    le_strings 里字符按 u16 大端(BE) 存储：
        ASCII '[' slot=0x5B  -> 内存字节 00 5B
        汉字 你  slot=403    -> 内存字节 01 93
    所以：
      · 搜 ASCII 片段要用 UTF-16BE 编码（不是 LE，也不是单字节）
      · 搜中文必须手工 pack('>H', charlist索引+0x20)，因为存的是索引不是码点
      · 另搜一份 UTF-16LE 的真 Unicode，用来判断游戏是否已把 slot 转成 Unicode
"""

import os, sys, struct, re, time

PROCNAME = "SR2_pc.exe"

# ---------- Windows API ----------
import ctypes
from ctypes import wintypes, byref, sizeof, create_string_buffer

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
READABLE = {0x02, 0x04, 0x20, 0x40}          # RO / RW / EXEC_READ / EXEC_RW

MAX_ADDR = 0x80000000                        # 32 位进程用户态上限


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


# ---- 明确函数签名 ----
# ★ 关键：ctypes 默认把 Python int 按 c_int(32位) 传参，指针会被截断，
#   必须显式声明 argtypes，否则 WriteProcessMemory / VirtualAllocEx 会莫名失败。
P_SZ = ctypes.POINTER(ctypes.c_size_t)

ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                              ctypes.c_size_t, P_SZ]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = k32.WriteProcessMemory
WriteProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                               ctypes.c_size_t, P_SZ]
WriteProcessMemory.restype = wintypes.BOOL

VirtualAllocEx = k32.VirtualAllocEx
VirtualAllocEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t,
                           wintypes.DWORD, wintypes.DWORD]
VirtualAllocEx.restype = ctypes.c_void_p

VirtualFreeEx = k32.VirtualFreeEx
VirtualFreeEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD]
VirtualFreeEx.restype = wintypes.BOOL

VirtualQueryEx = k32.VirtualQueryEx
VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                           ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
VirtualQueryEx.restype = ctypes.c_size_t

OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE


def is_wow64(h):
    """目标进程是不是 32 位（跑在 Wow64 上）"""
    try:
        IsWow64Process = k32.IsWow64Process
        IsWow64Process.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
        IsWow64Process.restype = wintypes.BOOL
        flag = wintypes.BOOL()
        if IsWow64Process(h, byref(flag)):
            return bool(flag.value)
    except Exception:
        pass
    return False


def addr_limit(h):
    """扫描地址上限：32 位进程到 0x7FFFFFFF，64 位进程放宽到用户态上限"""
    return 0x7FFFFFFF if is_wow64(h) else 0x7FFFFFFFFFFF


def enable_debug_privilege():
    """尽力提权 SeDebugPrivilege（不是必须，失败也继续）"""
    try:
        TOKEN_ADJUST_PRIVILEGES = 0x0020
        TOKEN_QUERY = 0x0008
        SE_PRIVILEGE_ENABLED = 0x0002

        class LUID(ctypes.Structure):
            _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", ctypes.c_long)]

        class LUID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]

        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", wintypes.DWORD),
                        ("Privileges", LUID_AND_ATTRIBUTES * 1)]

        htok = wintypes.HANDLE()
        if not advapi32.OpenProcessToken(k32.GetCurrentProcess(),
                                         TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, byref(htok)):
            return False
        luid = LUID()
        advapi32.LookupPrivilegeValueW(None, "SeDebugPrivilege", byref(luid))
        tp = TOKEN_PRIVILEGES()
        tp.PrivilegeCount = 1
        tp.Privileges[0].Luid = luid
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        ok = advapi32.AdjustTokenPrivileges(htok, False, byref(tp), 0, None, None)
        k32.CloseHandle(htok)
        return bool(ok)
    except Exception:
        return False


def list_processes(filter_name=None):
    snap = k32.CreateToolhelp32Snapshot(0x00000002, 0)     # TH32CS_SNAPPROCESS
    if snap == ctypes.c_void_p(-1).value:
        return []
    pe = PROCESSENTRY32()
    pe.dwSize = sizeof(PROCESSENTRY32)
    out = []
    try:
        ok = k32.Process32First(snap, byref(pe))
        while ok:
            name = pe.szExeFile.decode("ascii", "replace")
            if not filter_name or filter_name.lower() in name.lower():
                out.append((pe.th32ProcessID, name))
            ok = k32.Process32Next(snap, byref(pe))
    finally:
        k32.CloseHandle(snap)
    return out


def open_process(pid):
    access = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    h = OpenProcess(access, False, pid)
    if not h:
        # 退一步只申请读权限试试
        h = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        raise RuntimeError("OpenProcess 失败, err=%d (权限不足请以管理员身份运行终端)" % ctypes.get_last_error())
    return h


def enum_regions(h, max_addr):
    """产出 (base, size, protect) 的已提交且可读区域"""
    addr = 0x10000
    mbi = MEMORY_BASIC_INFORMATION()
    while addr < max_addr:
        if not VirtualQueryEx(h, ctypes.c_void_p(addr), byref(mbi), sizeof(mbi)):
            break
        base = mbi.BaseAddress or 0
        size = mbi.RegionSize or 0
        if size == 0:
            break
        if (mbi.State == MEM_COMMIT and (mbi.Protect & PAGE_GUARD) == 0
                and mbi.Protect in READABLE):
            yield base, size, mbi.Protect
        nxt = base + size
        if nxt <= addr:
            break
        addr = nxt


def read_mem(h, addr, n):
    buf = create_string_buffer(n)
    got = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, byref(got))
    if not ok:
        return None
    return buf.raw[:got.value]


PROGRESS_STEP = 200 * 1024 * 1024       # 每读这么多报一次进度
OUTDIR = r"F:/sr2-cn/_扫描结果"


class Tee(object):
    """把 print 同时写到控制台和文件里，避免输出滚屏丢失"""

    def __init__(self, path):
        self.f = open(path, "w", encoding="utf-8")
        self.console = sys.stdout

    def write(self, s):
        self.console.write(s)
        try:
            self.f.write(s)
            self.f.flush()
        except Exception:
            pass

    def flush(self):
        self.console.flush()
        try:
            self.f.flush()
        except Exception:
            pass


# ---------- 字表 ----------
def load_charlist():
    sys.path.insert(0, "F:/sr2-cn")
    import sr2lib as S
    game = "G:/SteamLibrary/steamapps/common/Saints Row 2/"
    vp = S.Vpp(game + "patch.vpp_pc")
    buf = vp.read(vp.find("charlist_CH", "txt"))
    end = buf.find(b"//ENDOFFILE")
    cl = [int(x) for x in re.findall(rb"\d+", buf[:end if end > 0 else len(buf)])]
    del vp
    return cl


CL = None


def be(s):
    """字符串 -> UTF-16BE 字节（用于搜 ASCII slot 序列）"""
    return s.encode("utf-16-be")


def le(s):
    """字符串 -> UTF-16LE 字节（用于搜真正的 Unicode）"""
    return s.encode("utf-16-le")


def slots_be(text):
    """中文/ASCII 混排文本 -> slot BE 字节流（汉字用 charlist 索引+0x20）"""
    cp2 = {cp: i + 0x20 for i, cp in enumerate(CL)}
    out = b""
    for ch in text:
        o = ord(ch)
        out += struct.pack(">H", o if 0x20 <= o <= 0x7E else cp2[o])
    return out


def decode_slots(raw):
    """把 slot BE 字节流尽力解成可读文本"""
    out = []
    for i in range(0, len(raw) - 1, 2):
        s = struct.unpack_from(">H", raw, i)[0]
        if s == 0:
            out.append("<END>")
            continue
        if 0x20 <= s <= 0x7E:
            out.append(chr(s))
        else:
            ci = s - 0x20
            out.append(chr(CL[ci]) if 0 <= ci < len(CL) else "<%#x>" % s)
    return "".join(out)


def build_patterns():
    """所有要搜的模式。每个都能独立给出一条结论。"""
    P = []
    # 1) 中文 REC1 开头：你 的 [ f —— 只可能出现在中文表里
    P.append(("CH_你的[format]", slots_be("你的") + be("[f"), "中文表独有"))
    # 2) 中文 REC1 中部：弟兄们 后紧跟 [/format]
    P.append(("CH_弟兄们[/format]", slots_be("弟兄们") + be("[/f"), "中文表独有"))
    # 3) 完整的 [format][color:green] 标签 BE 字节（CH 和 US 表都会命中）
    P.append(("tag_green_BE", be("[format][color:green]"), "CH/US 都会命中"))
    # 4) 乱码串的真 Unicode LE —— 检验「第二数据源」假说
    P.append(("乱码_任璨偶巧位_LE", le("任璨偶巧位"), "有结果=内存里真有这串中文"))
    # 5) 乱码串前 3 字，容错更强
    P.append(("乱码_任璨_LE", le("任璨"), "同上（更宽松）"))
    # 6) 中文全文真 Unicode LE —— 有结果说明游戏已转成 Unicode
    P.append(("CH全文_LE", le("你的弟兄们需要你的保护"), "有结果=slot已被转成Unicode"))
    # 7) 英文原文（单字节 ASCII）—— 定位 US 表做对照
    P.append(("EN_homies", b"homies", "英文表，用于对照"))
    # 8) ASCII 探针残留（若之前装过探针）
    P.append(("probe_ABCDE", be("ABCDEFGHIJK"), "若之前装过ASCII探针"))
    return P


def scan_process(h, patterns, max_addr):
    maxlen = max(len(p[1]) for p in patterns)
    overlap = maxlen - 1
    chunk = 0x400000                      # 4MB
    results = {p[0]: [] for p in patterns}
    total = 0
    scanned = 0
    nregions = 0
    t0 = time.time()
    next_tick = PROGRESS_STEP
    tick_base = 0
    for base, size, prot in enum_regions(h, max_addr):
        nregions += 1
        total += size
        pos = 0
        prev_tail = b""
        while pos < size:
            want = min(chunk, size - pos)
            raw = read_mem(h, base + pos, want)
            if raw is None:
                pos += want
                prev_tail = b""
                continue
            data = prev_tail + raw
            for name, pat, note in patterns:
                start = 0
                while True:
                    i = data.find(pat, start)
                    if i < 0:
                        break
                    # 命中地址要减掉 prev_tail 的偏移
                    addr = base + pos + i - len(prev_tail)
                    results[name].append(addr)
                    start = i + 1
                    if len(results[name]) > 40:
                        break
            prev_tail = data[-overlap:] if overlap > 0 else b""
            pos += want
            scanned += want
            if scanned - tick_base >= next_tick:
                tick_base = scanned
                print("    ...已扫 %.0f MB / 已命中 %d 处 (%.0f 秒)" % (
                    scanned / 1e6, sum(len(v) for v in results.values()), time.time() - t0))
    dt = time.time() - t0
    return results, scanned, total, dt, nregions


def classify_enc_hit(h, addr, pat):
    """判定这一处 Unicode 命中是「真 LE 字符串」还是「BE 数据的错位命中」。

    ★ 关键陷阱：UTF-16BE 与 UTF-16LE 在内存里只差【一个字节】。
      ASCII 字符的 UTF-16 必然有一个字节是 00：
          '[' 的 BE = 00 5B        它的 LE = 5B 00
      于是一段 BE 数据 `00 5B 00 66 …` 从下一个字节读，恰好就是 LE 的 `5B 00 66 00 …`
      → 搜 LE 必然在 BE 数据的 (起始+1) 处再命中一次。
      若不甄别，会把同一份数据误判成"LE 和 BE 各一份"，进而错判第二数据源。

    ★ 但注意：这只对【纯 ASCII】串成立。
      汉字「任」U+4EFB 的 BE = 4E FB，两个字节都非零，错位后不会得到 LE 的形式，
      所以搜中文完全不会错位（实测确认：BE 存储的汉字，搜 LE 命中 0 处）。
      => 对中文结论可以放心；需要甄别的是 [format][color:green] 这类 ASCII 标签。
    """
    if len(pat) < 2:
        return "模式太短，无法甄别"
    prev2 = read_mem(h, addr - 1, 2)
    if prev2 and len(prev2) == 2 and bytes([pat[1], pat[0]]) == prev2:
        # ★ 注意：这里是【信息论上不可区分】的两种解读，不是"谁真谁假"。
        #   0x00 + LE串 拼出来的字节 == BE串 的字节，物理上完全相同的数据。
        #   处理办法是【去重】：标注为同一份，避免把它当成第二数据源。
        return "← 同一份数据的另一种字节序解读（同一份！串在 0x%X 起，别算成两份）" % (addr - 1)
    nxt2 = read_mem(h, addr + len(pat), 2)
    if nxt2 and len(nxt2) == 2 and struct.unpack("<H", nxt2)[0] == 0:
        return "← 本字节序的真字符串（后随 00 00 终止符）"
    prev_chk = bytes([pat[1], pat[0]]) if len(pat) >= 2 else b""
    return "← 待人工判断（前一字节=%s，非错位）" % (prev2 or b"").hex().upper()


def report(h, results, patterns, scanned, total, dt, nreg=0):
    print("=" * 78)
    print("扫描完成：%.1f 秒内读 %.0f MB（%d 个可读区共 %.0f MB）" % (
        dt, scanned / 1e6, nreg, total / 1e6))
    print("=" * 78)
    for name, pat, note in patterns:
        addrs = results[name]
        print("\n【%s】命中 %d 处    %s" % (name, len(addrs), note))
        for a in addrs[:8]:
            extra = ""
            if name.endswith("_LE") and len(pat) >= 4:
                # ★ Unicode 类搜索必须甄别字节序错位，否则一份数据会被当成两份
                extra = "   " + classify_enc_hit(h, a, pat)
            print("    0x%08X%s" % (a, extra))
    print()

    # 重点：若找到中文表，dump 上下文
    key = "CH_你的[format]"
    if results[key]:
        print("=" * 78)
        print("★ 找到中文表活动串，解析上下文：")
        for a in results[key][:5]:
            base = a - 12                      # 往前 12 字节 = ID(4) + 你(2) 的(2) + ... 实际看情况
            raw = read_mem(h, base, 120)
            if raw is None:
                continue
            id1, id2 = struct.unpack_from("<HH", raw, 0)
            print("\n  命中地址 0x%08X" % a)
            print("    前 12 字节 ID 字段: %s  ->  hash=0x%08X %s" % (
                raw[:12].hex(" ").upper(), (id1 << 16) | id2,
                "★ 正是目标 REC1" if ((id1 << 16) | id2) == 0x84F287ED else ""))
            print("    整条解码: %s" % decode_slots(raw[4:]))
            print("    原始字节: %s" % raw[:60].hex(" ").upper())
    else:
        print("\n⚠ 未找到「你的[format」—— 中文表可能尚未加载到内存。")
        print("   请确认：已进游戏、且至少进入过一次能触发中文文本的界面。")

    gr = results.get("乱码_任璨偶巧位_LE") or results.get("乱码_任璨_LE")
    print("\n" + "=" * 78)
    if gr:
        print("★ 内存里搜到【乱码中文】的真 Unicode —— 这串汉字确实存在于内存中")
        print("  （上面的甄别会说明它是 UTF-16BE 还是 LE；错位命中=同一份数据，不算两份）")
        print("  注意：这份数据【不是】le_strings 里的 slot 编码（slot 存的是字表索引），")
        print("  所以它是独立的第二数据源（很可能是同步到内存的 HUD 文本缓冲）。")
        print("  下一步：对这些地址下访问断点，即可抓到写它的代码 → 字形重排发生的地点。")
    else:
        print("★ 内存里【没有】乱码中文 —— 印证：屏幕乱码是渲染期字形重排的产物，")
        print("   内存中存的仍是正确的 slot 序列，不存在第二个中文文本源。")
        print("   （若同时也没搜到「你的[format」，说明表还没加载，不算数）")


def cmd_ps():
    ps = list_processes()
    hit = [p for p in ps if PROCNAME.lower() in p[1].lower()]
    print("进程总数 %d" % len(ps))
    if hit:
        print("★ 目标进程:")
        for pid, name in hit:
            print("   pid=%-8d %s" % (pid, name))
    else:
        print("⚠ 未找到 %s —— 请先启动游戏" % PROCNAME)
        print("包含 'sr' 的进程：")
        for pid, name in list_processes("sr")[:20]:
            print("   pid=%-8d %s" % (pid, name))


def cmd_selfcheck():
    """正本自检：在本进程里远程分配内存写入已知标记，再扫描确认能搜到。
    ★ 铁律：搜索类工具必须先在正样本上验证，否则『搜不到』毫无意义。"""
    pid = os.getpid()
    print("自检目标：本 python 进程 pid=%d" % pid)
    enable_debug_privilege()
    h = open_process(pid)

    marker_text = "SR2SELFCHECKMARK"
    marker = be(marker_text)                      # UTF-16BE 形式
    MEM_COMMIT_RESERVE = 0x3000
    PAGE_READWRITE = 0x04
    remote = VirtualAllocEx(h, None, 4096, MEM_COMMIT_RESERVE, PAGE_READWRITE)
    if not remote:
        print("VirtualAllocEx 失败 err=%d" % ctypes.get_last_error())
        return
    mbuf = create_string_buffer(marker, len(marker))
    written = ctypes.c_size_t(0)
    ok = WriteProcessMemory(h, ctypes.c_void_p(remote), mbuf, len(marker), byref(written))
    print("已在 0x%08X 写入标记 %r (%d 字节, 实际写入 %d, %s)" % (
        remote, marker_text, len(marker), written.value, "成功" if ok else "失败"))
    if not ok:
        return

    # 回填一点填充，避免整页全零被优化
    patterns = [("SELFCHECK_BE", marker, "刚写入的 UTF-16BE 标记")]
    lim = addr_limit(h)
    print("目标位数: %s, 扫描上限 0x%X" % ("32 位" if lim == 0x7FFFFFFF else "64 位", lim))
    res, scanned, total, dt, nreg = scan_process(h, patterns, lim)
    hits = res["SELFCHECK_BE"]
    print("扫描 %.1f 秒 / %.0f MB (%d 个可读区) -> 命中 %d 处" % (
        dt, scanned / 1e6, nreg, len(hits)))
    if hits:
        print("★ 自检通过，命中地址：" + ", ".join("0x%08X" % a for a in hits[:5]))
        raw = read_mem(h, hits[0], len(marker) + 8)
        print("   读回内容: %s" % (raw or b"").hex(" ").upper()[:80])
        print("   解码    : %r" % (raw or b"").decode("utf-16-be", "replace"))
    else:
        print("✗ 自检失败：明明写了却搜不到，工具链路有问题")
    VirtualFreeEx(h, ctypes.c_void_p(remote), 0, 0x8000)     # MEM_RELEASE
    k32.CloseHandle(h)


def cmd_dump(addr):
    if isinstance(addr, str):
        addr = int(addr, 0)
    h = open_process(find_pid())
    raw = read_mem(h, addr - 32, 160)
    if raw is None:
        print("读取失败")
        return
    print("地址 0x%08X 附近 160 字节：" % addr)
    for off in range(0, 160, 16):
        chunk = raw[off:off + 16]
        line = "  %08X  %-47s  %s" % (
            addr - 32 + off,
            chunk.hex(" ").upper(),
            "".join(chr(c) if 32 <= c < 127 else "." for c in chunk))
        print(line)
    print("\n按 slot(BE) 解码(@+0): %s" % decode_slots(raw[32:]))
    try:
        print("按 UTF-16LE 解码  : %r" % raw[32:96].decode("utf-16-le", "replace"))
    except Exception:
        pass


def find_pid():
    hit = [p for p in list_processes() if PROCNAME.lower() in p[1].lower()]
    if not hit:
        raise RuntimeError("未找到 %s，请先启动游戏" % PROCNAME)
    return hit[0][0]


def run_scan():
    """完整扫描流程"""
    global CL
    enable_debug_privilege()
    pid = find_pid()
    print("目标进程 pid=%d  (%s)" % (pid, PROCNAME))
    h = open_process(pid)
    print("已打开进程句柄")
    CL = load_charlist()
    print("字表 %d 项已加载" % len(CL))
    patterns = build_patterns()
    lim = addr_limit(h)
    print("目标位数: %s，扫描上限 0x%X" % ("32 位" if lim == 0x7FFFFFFF else "64 位", lim))
    print("开始扫描 —— 游戏可以继续跑，字幕不需要此刻出现在屏幕上")
    print("（字符串表整表常驻内存，与字幕显示时机无关）\n")
    results, scanned, total, dt, nreg = scan_process(h, patterns, lim)
    report(h, results, patterns, scanned, total, dt, nreg)
    k32.CloseHandle(h)


def cmd_wait(timeout=900):
    """先等游戏出现再自动开扫 —— 可以先运行脚本，再从容地启动游戏"""
    print("等待 %s 启动（最多 %d 秒）……可以现在去开游戏" % (PROCNAME, timeout))
    t0 = time.time()
    while time.time() - t0 < timeout:
        hit = [p for p in list_processes() if PROCNAME.lower() in p[1].lower()]
        if hit:
            print("\n★ 检测到 %s (pid=%d)" % (hit[0][1], hit[0][0]))
            print("  等 5 秒让字符串表加载进内存……")
            time.sleep(5)
            run_scan()
            return
        time.sleep(2)
    print("超时：%d 秒内没等到游戏启动" % timeout)


def main():
    global CL
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "ps":
        cmd_ps()
        return
    if cmd == "selfcheck":
        cmd_selfcheck()
        return
    if cmd == "dump":
        CL = load_charlist()
        cmd_dump(sys.argv[2])
        return

    # 落盘：输出同时写文件，防止命令行窗口缓冲被清掉
    try:
        os.makedirs(OUTDIR, exist_ok=True)
        logpath = os.path.join(
            OUTDIR, "scan_%s.txt" % time.strftime("%Y%m%d_%H%M%S"))
        sys.stdout = Tee(logpath)
        _LOGS.append(logpath)
    except Exception as ex:
        print("(无法创建日志文件: %s)" % ex)

    try:
        if cmd == "wait":
            cmd_wait()
        else:
            run_scan()
    except RuntimeError as ex:
        print("\n⚠ %s" % ex)
    except Exception as ex:
        import traceback
        print("\n✗ 出错: %s" % ex)
        traceback.print_exc()

    if _LOGS:
        print("\n本次输出已保存到: %s" % _LOGS[-1])
        sys.stdout.flush()

_LOGS = []


if __name__ == "__main__":
    main()
