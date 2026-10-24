import shutil, hashlib, datetime, os
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
cur=game+"patch.vpp_pc"
new=r"F:/sr2-cn/_v534_build.vpp_pc"
assert hashlib.md5(open(new,'rb').read()).hexdigest()=='2fd6a5e9d517971e2135c5a34c6daf68'
ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak=game+f"patch.vpp_pc.v{ts}_before_v534.bak"
shutil.copy2(cur,bak)
shutil.copy2(new,cur)
print("备份当前(953ce862,含无效tagfix):",bak)
print("已部署 v534, md5:",hashlib.md5(open(cur,'rb').read()).hexdigest())
print("size:",os.path.getsize(cur))
