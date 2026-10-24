# -*- coding: utf-8 -*-
"""验证新增三项：Tee 落盘 / wait 超时 / 进度提示（按铁律先在正样本上自检）"""
import sys, os
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

print("=== 1) 语法/导入 OK, PROGRESS_STEP=%d, OUTDIR=%s ===" % (C.PROGRESS_STEP, C.OUTDIR))

# --- 2) Tee 能否同时写控制台和文件 ---
os.makedirs(C.OUTDIR, exist_ok=True)
tmp = os.path.join(C.OUTDIR, "_test_tee.txt")
old = sys.stdout
sys.stdout = C.Tee(tmp)
print("这行应同时出现在屏幕和文件里")
sys.stdout.flush()
sys.stdout = old
content = open(tmp, encoding="utf-8").read()
print("落盘内容: %r" % content)
assert "这行应同时出现" in content, "Tee 落盘失败"
print("★ Tee 落盘正常")

# --- 3) wait 超时路径 ---
sys.stdout = C.Tee(os.path.join(C.OUTDIR, "_test_wait.txt"))
C.cmd_wait(timeout=4)
sys.stdout.flush()
sys.stdout = old
w = open(os.path.join(C.OUTDIR, "_test_wait.txt"), encoding="utf-8").read()
print("wait 输出: %r" % w)
assert "超时" in w, "wait 超时路径异常"
print("★ wait 未等到游戏 -> 正确提示超时")

# --- 4) 进度提示（把阈值调到 1MB 触发）---
C.PROGRESS_STEP = 1 * 1024 * 1024
import time
t0 = time.time()
pid = os.getpid()
h = C.open_process(pid)
res, scanned, total, dt, nreg = C.scan_process(
    h, [("NONEXIST", b"@@@@NEVERMATCH@@@@", "负样本")], C.addr_limit(h))
C.k32.CloseHandle(h)
print("★ 负样本扫描: %.1f 秒 %d 区 %.0f MB -> 命中 %d (应为0)" % (dt, nreg, scanned/1e6, len(res["NONEXIST"])))
assert not res["NONEXIST"], "负样本不应命中"

# --- 5) 清理 ---
os.remove(tmp); os.remove(os.path.join(C.OUTDIR, "_test_wait.txt"))
print("\n全部自检通过")
