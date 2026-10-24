# DLC 汉化源资料

translations_dlc.py 保存补译词条；gen_dlc_ch2.py 和 rebuild4.py 等是 2026-10 的原始重建记录，含本机绝对路径，作为算法依据保留。
当前可直接部署的 982 条 slot 编码中文表在 localization/payload/DLC/Text/dlc_ch.le_strings。
可编辑的完整文本导出在 localization/text/dlc_ch.json；字符表位于 localization/text/charlist_CH.json。
文本以字符表索引 + 0x20 编码，不能直接把 Unicode 中文写入 le_strings。
