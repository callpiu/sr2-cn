# -*- coding: utf-8 -*-
"""
★★★ SR2 活动字幕乱码 · 运行时取证（第九轮最终版）

用法（推荐先跑脚本再去开游戏）：
    cd /f/sr2-cn
    ./.venv/Scripts/python.exe _RT_charlist_final.py wait

或者游戏已经在运行：
    ./.venv/Scripts/python.exe _RT_charlist_final.py

跑完把屏幕输出【整段复制】发给我即可；
同时结果也存到了：F:/sr2-cn/_rt_final.txt  和  F:/sr2-cn/_rt_final.json
"""
import sys, os, struct, json, time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

OUTJSON = "F:/sr2-cn/_rt_final.json"
OUTTXT  = "F:/sr2-cn/_rt_final.txt"

# ---------------- 关键全局地址（SR2_pc.exe，ImageBase=0x400000，无 ASLR） ----------------
LANG_VA   = 0xE8C470      # 语言码（-1=未初始化；0=US；13=CH）
FONT_INIT = 0x2528B0F     # 字体/字符表初始化标志
CC_LIST   = 0x2528B2C     # charlist 指针
CC_CNT    = 0x2528B30     # charlist 项数
ALIEN     = 0x2528B28     # “出现外来字符”标志

LANG_NAMES = ["US","ES","IT","JP","DE","FR","NL","SE","DK","CZ","PL","SK","RU","CH"]

_LINES = []


def log(s=""):
    print(s)
    _LINES.append(s)


def disk_charlist_strict():
    """按引擎逻辑严格解析磁盘 charlist_CH：跳过 // 行，count= 取数，逐行取码点。"""
    from sr2lib import Vpp
    G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
    v = Vpp(G + "/patch.vpp_pc")
    b = v.read(v.find("charlist_CH", "txt"))
    del v
    cps, started = [], False
    for ln in b.replace(b"\r\n", b"\n").split(b"\n"):
        s = ln.strip()
        if not s or s.startswith(b"//"):
            continue
        if s.lower().startswith(b"count="):
            started = True
            continue
        if not started:
            continue
        if s.isdigit():
            cps.append(int(s))
    return cps


def rd(h, addr, fmt="<i"):
    n = struct.calcsize(fmt)
    r = C.read_mem(h, addr, n)
    if r is None or len(r) < n:
        return None
    return struct.unpack(fmt, r)[0]


def scan_utf16le(h, text, cap=6):
    pat = text.encode("utf-16-le")
    hits = []
    for base, size, prot in C.enum_regions(h, C.addr_limit(h)):
        pos, tail = 0, b""
        while pos < size:
            want = min(0x400000, size - pos)
            raw = C.read_mem(h, base + pos, want)
            if raw is None:
                pos += want; tail = b""; continue
            data = tail + raw
            s = 0
            while True:
                i = data.find(pat, s)
                if i < 0:
                    break
                hits.append(base + pos + i - len(tail))
                s = i + 1
                if len(hits) >= cap:
                    return hits
            tail = data[-len(pat):]
            pos += want
    return hits


def main(wait=False):
    ev = {"ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    log("=" * 70)
    log("SR2 活动字幕乱码 · 运行时取证     " + ev["ts"])
    log("=" * 70)

    if wait:
        log("等待 SR2_pc.exe 启动（最多 15 分钟）……")
        t0 = time.time()
        while time.time() - t0 < 900:
            if [p for p in C.list_processes() if "sr2_pc.exe" in p[1].lower()]:
                log("检测到游戏，等 10 秒让字符表加载……")
                time.sleep(10)
                break
            time.sleep(2)
        else:
            log("✗ 超时：15 分钟内没检测到游戏。请先启动游戏再运行本脚本。")
            return

    C.enable_debug_privilege()
    pid = C.find_pid()
    log("★ 目标进程 pid = %d" % pid)
    ev["pid"] = pid
    h = C.open_process(pid)

    # ---------------- A. 语言码 ----------------
    lang = rd(h, LANG_VA, "<i")
    ev["lang_code"] = lang
    nm = LANG_NAMES[lang] if (lang is not None and 0 <= lang < len(LANG_NAMES)) else "?"
    log("")
    log("【A】语言码 [0x%08X] = %s  -> %s" % (LANG_VA, lang, nm))
    if lang == -1:
        log("     ★★ 语言码 = -1：loadcharlist 会在 0x7F4455 直接跳过整张字符表！")
    elif lang == 0:
        log("     ★★ 语言码 = 0 (US)：引擎会去开 charlist_US.txt —— 该文件不存在！")
    elif lang == 13:
        log("     ✓ 语言码 = 13 (CH)：引擎会开 charlist_CH.txt（正确）")
    elif lang is not None:
        log("     ! 语言码 = %s：引擎会开 charlist_%s.txt" % (lang, nm))

    fi = rd(h, FONT_INIT, "<B")
    ev["font_init_flag"] = fi
    log("")
    log("【B】字符表初始化标志 [0x%08X] = %s" % (FONT_INIT, fi))

    alien = rd(h, ALIEN, "<B")
    ev["alien_flag"] = alien
    log("    “出现外来字符”标志 [0x%08X] = %s" % (ALIEN, alien))

    # ---------------- C. 运行时字符表 ----------------
    num = rd(h, CC_CNT, "<I")
    ptr = rd(h, CC_LIST, "<I")
    ev["cc_num"] = num
    ev["cc_ptr"] = ptr
    log("")
    log("【C】运行时字符表：num[0x%08X]=%s   ptr[0x%08X]=0x%X" % (
        CC_CNT, num, CC_LIST, ptr or 0))

    ok = (num is not None and ptr is not None and 0 < num < 40000
          and 0x10000 < ptr < 0x80000000)
    if not ok:
        log("     ★★★ 字符表【未加载 / 为空】(num=%s) —— 这就是乱码的直接原因！" % num)
        log("         引擎没能加载 charlist_CH.txt。")
        log("         结合【A】：若语言码为 -1 或 0(US) → 根因即语言码。")
    else:
        raw = C.read_mem(h, ptr, num * 4)
        pairs = struct.unpack("<%dH" % (num * 2), raw)
        entries = [(pairs[i*2], pairs[i*2+1]) for i in range(num)]
        log("     读回 %d 项（struct: <u16 codepoint, u16 glyph>）" % len(entries))
        log("     前 8 项: " + str([(hex(u), hex(g)) for u, g in entries[:8]]))
        log("     末 4 项: " + str([(hex(u), hex(g)) for u, g in entries[-4:]]))

        # ASCII 前缀长度
        pref, exp = 0, 0x20
        for u, g in entries:
            if u == exp:
                pref += 1; exp += 1
            else:
                break
        ev["rt_ascii_prefix"] = pref
        log("     ★ 运行时 ASCII 前缀长度 = %d   （磁盘期望 224）" % pref)

        # 与磁盘对比
        dc = disk_charlist_strict()
        ev["disk_len"] = len(dc)
        n = min(len(dc), num)
        diff = next((i for i in range(n) if dc[i] != entries[i][0]), None)
        ev["first_diff_index"] = diff
        log("     磁盘 charlist_CH（严格解析）= %d 项" % len(dc))
        if diff is None and len(dc) == num:
            log("     ★ 运行时表与磁盘【完全一致】→ 表加载正确，问题在渲染/字体")
        elif diff is None:
            log("     ★ 前 %d 项一致（长度差 %d）" % (n, num - len(dc)))
        else:
            log("     ★★ 第 %d 项起不一致：" % diff)
            for i in range(diff, min(diff + 5, n)):
                log("        [%d] 运行时=U+%04X  磁盘=U+%04X" % (
                    i, entries[i][0], dc[i]))

    # ---------------- D. 内存中文搜索 ----------------
    log("")
    log("【D】内存中文搜索（UTF-16LE 真 Unicode）")
    for lbl, t in (("正确『你的弟兄们』", "你的弟兄们"),
                   ("乱码『任璨』", "任璨"),
                   ("乱码『任璨偶巧位』", "任璨偶巧位")):
        hs = scan_utf16le(h, t)
        ev["mem_" + lbl] = [hex(x) for x in hs]
        log("   %-22s 命中 %2d 处  %s" % (lbl, len(hs), [hex(x) for x in hs[:4]]))

    log("")
    log("========== 取证结束 ==========")
    log("请把以上【整段输出】发给我。")

    try:
        with open(OUTJSON, "w", encoding="utf-8") as f:
            json.dump(ev, f, ensure_ascii=False, indent=1)
        with open(OUTTXT, "w", encoding="utf-8") as f:
            f.write("\n".join(_LINES))
        log("（已保存 %s / %s）" % (OUTJSON, OUTTXT))
    except Exception as e:
        log("保存失败: %s" % e)

    C.k32.CloseHandle(h)


if __name__ == "__main__":
    main(wait=(len(sys.argv) > 1 and sys.argv[1] == "wait"))
