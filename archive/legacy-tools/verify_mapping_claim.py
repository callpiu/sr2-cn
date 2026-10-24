"""回应核查文档：验证「字形映射在两条串里一致」这个论证是否成立。

核查文档的论证
    REC1 中文: 你 的 弟 兄 们 需 要 你 的 保 护
    REC1 乱码: 任 璨 偶 巧 位 雄 衡 任 璨 伪 该

    REC2 中文: 你 的 弟 兄 们 要 出 去 谈 几 笔 生 意 ， 保 护 他 们 免 遭 袭 击
    REC2 乱码: 任 璨 偶 巧 位 校 衡 勾 远 藐 乱 携 ？ 空 伪 该 亡 位 通 像 匪 冰 挺 拮

    声称：你→任 的→璨 弟→偶 兄→巧 们→位 保→伪 护→该
          「7 个字在两条独立记录里映射到同一个字」

本脚本
    把两条串的【期望字 → 观测字】映射逐位列出，
    检查是否存在【同一期望字映射到不同观测字】的矛盾。
"""
import os, sys

# 用户报告的乱码（来自多张截图，取最完整的一次）
REC1_WANT = "你的弟兄们需要你的保护"
REC1_GOT  = "任璨偶巧位雄衡任璨伪该"          # 12 字（用户首次报告）

REC2_WANT = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
REC2_GOT  = "任璨偶巧位校衡勾远藐乱携 伪该亡位通像匪冰挺拮"   # 含空格

print("=== REC1 ===")
print("  期望(%d): %s" % (len(REC1_WANT), REC1_WANT))
print("  观测(%d): %s" % (len(REC1_GOT), REC1_GOT))
print()
print("=== REC2 ===")
print("  期望(%d): %s" % (len(REC2_WANT), REC2_WANT))
print("  观测(%d): %s" % (len(REC2_GOT), REC2_GOT))
print()

# REC1 映射
m1 = {}
print("REC1 逐位映射:")
for i, (a, b) in enumerate(zip(REC1_WANT, REC1_GOT)):
    m1.setdefault(a, set()).add(b)
    print("  %2d  %s -> %s" % (i, a, b))
print()

# REC2 映射（跳过观测里的空格，因为它可能是「，」渲染失败）
print("REC2 逐位映射（观测去掉空格后对齐）:")
got2 = REC2_GOT.replace(" ", "")
print("  REC2 期望 %d 字, 观测(去空格) %d 字" % (len(REC2_WANT), len(got2)))
m2 = {}
for i, (a, b) in enumerate(zip(REC2_WANT, got2)):
    m2.setdefault(a, set()).add(b)
    tgt = m1.get(a)
    flag = ""
    if tgt:
        if b in tgt:
            flag = "  ✓ 与 REC1 一致"
        else:
            flag = "  ★★ 与 REC1 冲突！(REC1: %s)" % "/".join(tgt)
    print("  %2d  %s -> %s%s" % (i, a, b, flag))
print()

print("=== 汇总：同一期望字是否映射到多个观测字 ===")
allch = sorted(set(m1) | set(m2))
conflict = 0
for ch in allch:
    s1 = m1.get(ch, set())
    s2 = m2.get(ch, set())
    both = s1 | s2
    if len(both) > 1:
        conflict += 1
        print("  ★ %s: REC1->%s  REC2->%s" % (ch, "/".join(sorted(s1)) or "-", "/".join(sorted(s2)) or "-"))
if conflict == 0:
    print("  无冲突 —— 映射一致（支持核查文档的论证）")
else:
    print("  %d 个字存在冲突（不支持「映射一致」的论证）" % conflict)
