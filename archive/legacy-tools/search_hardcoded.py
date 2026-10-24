# -*- coding: utf-8 -*-
"""补搜：把活动串中文按【UTF-8/UTF-16LE/BE/GBK】四种编码全盘搜（含 lua/xtbl/dll/exe），
文档只按 le_strings 槽位序列搜过，硬编码文本会被漏掉。"""
import os, sys, mmap

ROOT = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
WORDS = ["弟兄们", "免遭袭击", "谈几笔生意", "需要你的保护"]

def pats(w):
    return {
     "utf8":   w.encode('utf-8'),
     "utf16le":w.encode('utf-16-le'),
     "utf16be":w.encode('utf-16-be'),
     "gbk":    w.encode('gbk'),
    }

# 先在正样本上自检：当前 patch.vpp_pc 应能用 utf-16be 搜到？不——VPP 里是 slot 编码。
# 自检改为：确认四种编码字节长度与预期一致
for w in WORDS:
    p=pats(w)
    print(f"[自检] {w}: " + " ".join(f"{k}={v.hex()}" for k,v in p.items()))

SKIP_EXT={'.vpp_pc'}   # 先不扫大包（10GB），先扫所有其他文件
hits=[]
scanned=0; scanned_bytes=0
for dirpath,dirs,files in os.walk(ROOT):
    for fn in files:
        ext=os.path.splitext(fn)[1].lower()
        path=os.path.join(dirpath,fn)
        try:
            sz=os.path.getsize(path)
        except Exception: continue
        if ext in SKIP_EXT: continue
        if sz>200*1024*1024: continue
        scanned+=1; scanned_bytes+=sz
        try:
            with open(path,'rb') as f:
                data=f.read()
        except Exception: continue
        for w in WORDS:
            for k,v in pats(w).items():
                i=data.find(v)
                if i>=0:
                    hits.append((path,w,k,i,sz))
print(f"\n扫描文件数={scanned}  总字节={scanned_bytes/1e6:.1f} MB")
if hits:
    print("\n★ 命中：")
    for p,w,k,i,sz in hits:
        print(f"  {p}\n     词={w} 编码={k} 偏移={i} (文件 {sz} B)")
else:
    print("\n未命中（非 VPP 文件里没有硬编码的这些中文）")
