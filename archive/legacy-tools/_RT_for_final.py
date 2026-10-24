# -*- coding: utf-8 -*-
"""
SR2 活动字幕乱码 · 运行时全量取证（一次性拿全真相）

用法（在游戏【运行中】执行，何时都行，字幕不需要正在屏幕上）：
    cd /f/sr2-cn
    ./.venv/Scripts/python.exe _RT_for_final.py

产出 F:/sr2-cn/_rt_evidence.json + 控制台报告，包含：
  A. 引擎语言码 [0xE8C470]（-1=未初始化）
  B. 运行时字符表 cc_list [0x2528B2C] / 数量 [0x2528B30]
     - 逐项 dump (codepoint, slot)
     - 与磁盘 charlist_CH 对比：前 224 项是否 0x20..0xFF
     - 目标字符"你的弟兄们需要你的保护"在【运行时表】里的 index/slot
  C. 内存中搜【正确中文 Unicode】与【乱码中文 Unicode】是否存在
  D. 扫描内存里"你的兄弟们"类文本的 slot 序列

判读要点：
  - 若 B 中运行时表与磁盘 charlist_CH 不一致 → 就是表加载错了
  - 若 B 一致 → 表没问题，问题在渲染/字体，转 C/D 分析
"""
import sys, os, struct, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

OUT = "F:/sr2-cn/_rt_evidence.json"
ev = {"ts": time.strftime("%Y-%m-%d %H:%M:%S")}

# ---------- 磁盘 charlist_CH ----------
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
_v = Vpp(G + "/patch.vpp_pc")
DISK_CL = [int(t) for t in _v.read(_v.find("charlist_CH", "txt")).decode().split()
           if t.lstrip("-").isdigit()]
del _v
ev["disk_charlist_len"] = len(DISK_CL)
print("磁盘 charlist_CH: %d 项" % len(DISK_CL))

TARGET = "你的弟兄们需要你的保护"
SCREEN = "任璨偶巧位雄衡任璨伪该"

def pause(msg):
    print(msg)

# ---------- 进程 ----------
pid = C.find_pid()
print("pid =", pid)
ev["pid"] = pid
h = C.open_process(pid)

# ---------- A. 语言码 ----------
LANG_VA = 0xE8C470
try:
    lang = struct.unpack("<i", C.read_mem(h, LANG_VA, 4))[0]
except Exception as e:
    lang = None
ev["lang_code_at_E8C470"] = lang
print("\n[A] 引擎语言码 [0x%08X] = %s  (0=US,1=ES,2=IT,3=JP,4=DE,5=FR,6=NL,7=SE,8=DK,9=CZ,10=PL,11=SK,12=RU,13=CH)" % (LANG_VA, lang))

# ---------- B. 运行时字符表 ----------
PTR = 0x2528B2C
CNT = 0x2528B30
num = ptr = None
for attempt in range(5):
    num = struct.unpack("<I", C.read_mem(h, CNT, 4))[0]
    ptr = struct.unpack("<I", C.read_mem(h, PTR, 4))[0]
    if 0 < num < 30000 and 0x10000 < ptr < 0x80000000:
        break
    print("  ... 字表未就绪 (num=%s ptr=0x%X)，1秒后重试" % (num, ptr))
    time.sleep(1)

ev["rt_num"] = num
ev["rt_ptr"] = ptr
print("\n[B] 运行时字符表 cc_list=0x%08X  num=%s" % (ptr or 0, num))
if num and ptr and 0 < num < 30000 and 0x10000 < ptr < 0x80000000:
    raw = C.read_mem(h, ptr, num * 4)
    pairs = struct.unpack("<%dH" % (num * 2), raw)
    entries = [(pairs[i * 2], pairs[i * 2 + 1]) for i in range(num)]
    ev["rt_entries_head"] = entries[:40]
    ev["rt_entries_tail"] = entries[-10:]

    # 1) 表项结构判断: entry[0]/entry[1] 的关系
    same = sum(1 for u, g in entries if u == g)
    print("     entry[0]==entry[1] 的项数: %d/%d" % (same, num))
    print("     前 12 项:", [(hex(u), hex(g)) for u, g in entries[:12]])
    print("     末 4 项 :", [(hex(u), hex(g)) for u, g in entries[-4:]])

    # 2) entry[0] 是否 = 0x20..0xFF 前缀
    print("     entry[0] 前 12 是否 0x20..: %s" % all(
        entries[i][0] == 0x20 + i for i in range(min(12, num)) if entries[i][0] < 0x100))
    pref = 0
    exp = 0x20
    for u, g in entries:
        if u == exp:
            pref += 1
            exp += 1
        else:
            break
    ev["rt_ascii_prefix_len"] = pref
    print("     ★ 运行时表 ASCII 前缀长度 = %d" % pref)

    # 3) 目标字符在运行时表的位置
    u2i = {}
    for i, (u, g) in enumerate(entries):
        u2i.setdefault(u, i)
    print("     目标字符在运行时表:")
    for ch in dict.fromkeys(TARGET):
        i = u2i.get(ord(ch))
        if i is None:
            print("       %s U+%04X  不存在" % (ch, ord(ch)))
        else:
            print("       %s U+%04X  rt_index=%d  rt_slot=entry[1]=%d" % (
                ch, ord(ch), i, entries[i][1]))

    # 4) 与磁盘表对比
    diff = []
    for i in range(min(len(DISK_CL), num)):
        if DISK_CL[i] != entries[i][0]:
            diff.append(i)
    ev["rt_vs_disk_first_diff"] = diff[:10]
    print("     ★ 运行时 entry[0] 与磁盘 charlist_CH 首个不一致 index: %s" % diff[:10])
    if not diff:
        print("     => 运行时表与磁盘完全一致（至少前 %d 项）" % min(len(DISK_CL), num))
else:
    print("     ✗ 未能读取运行时字表：请先让游戏进入主菜单或游戏内")

# ---------- C. 内存搜索：正确/乱码 中文 Unicode ----------
def scan_utf16(h, text, enc="utf-16-le"):
    pat = text.encode(enc)
    hits = []
    for base, size, prot in C.enum_regions(h, C.addr_limit(h)):
        pos = 0
        tail = b""
        while pos < size:
            want = min(0x400000, size - pos)
            raw = C.read_mem(h, base + pos, want)
            if raw is None:
                pos += want; tail = b""; continue
            data = tail + raw
            s = 0
            while True:
                i = data.find(pat, s)
                if i < 0: break
                hits.append(base + pos + i - len(tail))
                s = i + 1
                if len(hits) > 20: return hits
            tail = data[-len(pat):] if len(pat) > 1 else b""
            pos += want
    return hits

print("\n[C] 内存搜索中文（LE 真 Unicode）")
for label, txt in [("正确_你的弟兄们", "你的弟兄们"),
                   ("正确_全文", TARGET),
                   ("乱码_任璨偶巧位", SCREEN),
                   ("乱码_任璨", "任璨")]:
    hits = scan_utf16(h, txt)
    ev["mem_" + label] = [hex(x) for x in hits[:10]]
    print("   %-18s 命中 %d 处 %s" % (label, len(hits), [hex(x) for x in hits[:5]]))

# ---------- 保存 ----------
try:
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("\n已保存:", OUT)
except Exception as e:
    print("保存失败:", e)

C.k32.CloseHandle(h)
print("\n===== 取证结束 =====")
