p=r"F:/sr2-cn/build_v21/static_CH.le_strings"
data=open(p,'rb').read()
print("file size",len(data))
# read around 8180..8900 both encodings
for enc in ('utf-16-be','utf-16-le'):
    seg=data[8180:8950]
    print(f"\n--- decode {enc} from 8180 ---")
    print(seg.decode(enc,'replace'))
