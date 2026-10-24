# -*- coding: utf-8 -*-
"""手工解析 MSF 7.00 PDB：超级块 -> 流目录 -> 流清单。"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
print("magic:", d[:32].rstrip(b"\x00").decode("ascii", "replace"))
block_size = struct.unpack("<I", d[32:36])[0]
num_blocks = struct.unpack("<I", d[40:44])[0]
num_dir_bytes = struct.unpack("<I", d[44:48])[0]
block_map_addr = struct.unpack("<I", d[52:56])[0]
print("block_size=%d num_blocks=%d num_dir_bytes=%d block_map_addr=%d" % (
    block_size, num_blocks, num_dir_bytes, block_map_addr))
BS = block_size


def blk(i):
    return d[i * BS:(i + 1) * BS]


# 读块链（每块末尾 4 字节是 next；注意 MSF 里目录链的块“不用”末尾指针？
# 实际 MSF 7.0: block map 是块号数组，可能跨多块，块间用末尾4字节链）
def read_chain(start, want_bytes=None):
    out = b""
    cur = start
    seen = set()
    while cur != 0xFFFFFFFF and cur not in seen:
        seen.add(cur)
        b = blk(cur)
        out += b[: BS - 4]
        cur = struct.unpack("<I", b[BS - 4: BS])[0]
        if want_bytes and len(out) >= want_bytes:
            break
    return out


# dir_data 是“目录块号”的列表（每 4 字节一个块号），不是目录内容本身
map_list = read_chain(block_map_addr, None)
print("dir block-number table bytes=%d" % len(map_list))
ndir_blocks = (num_dir_bytes + BS - 1) // BS
idxs = [struct.unpack("<I", map_list[4 * j: 4 * j + 4])[0] for j in range(ndir_blocks)]
print("目录块号: %s (共%d块)" % (idxs[:8], len(idxs)))
dir_data = b"".join(blk(i) for i in idxs)[:num_dir_bytes]
print("real dir bytes=%d" % len(dir_data))
num_streams = struct.unpack("<I", dir_data[0:4])[0]
print("num_streams =", num_streams)
sizes = []
off = 4
for i in range(num_streams):
    sz = struct.unpack("<I", dir_data[off:off + 4])[0]
    off += 4
    sizes.append(0 if sz == 0xFFFFFFFF else sz)
print("max size", max(sizes))
blocks = []
for i in range(num_streams):
    nb = (sizes[i] + BS - 1) // BS
    lst = [struct.unpack("<I", dir_data[off + 4 * j: off + 4 * j + 4])[0] for j in range(nb)]
    off += 4 * nb
    blocks.append(lst)
print("stream list (first 12):")
for i in range(min(12, num_streams)):
    print("  [%2d] size=%-8d blocks=%s" % (i, sizes[i], blocks[i][:5]))
pickle.dump({"BS": BS, "sizes": sizes, "blocks": blocks, "path": P},
            open(r"F:\sr2-cn\_pdb_dir.pkl", "wb"))
print("saved _pdb_dir.pkl")
# 打印流名（PDB stream 1 = PDB info，含 stream names 表）
