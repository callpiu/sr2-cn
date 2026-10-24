# -*- coding: utf-8 -*-
"""自洽扫描：确定 文本区起点 / 指针数组位置 / 桶表规模"""
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()
N = len(raw)

def parse_from(T):
    """从 T 解析 (hash,BE文本,0x0000) 到 EOF，成功返回条目列表"""
    o = T
    ents = []
    while o + 4 <= N:
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= N:
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        if len(cps) > 4000:
            return None
        ents.append((o - 4, h, ''.join(chr(c) for c in cps), len(cps)))
    return ents if o == N else None

cands = []
for T in range(0x1300, 0x1380):
    ents = parse_from(T)
    if not ents:
        continue
    M = len(ents)
    byT = {e[0] + 4: e for e in ents}
    for extra in (0, 4):          # 数组末尾到文本区之间可能有 0 或 4 字节
        A = T - extra - 4 * M
        if A < 8 or (A - 8) % 8:
            continue
        arr = [struct.unpack_from('<I', raw, A + i * 4)[0] for i in range(M)]
        hit = sum(1 for a in arr if a in byT)
        Nb = (A - 8) // 8
        bk = [struct.unpack_from('<II', raw, 0x08 + i * 8) for i in range(Nb)]
        s = sum(b[1] for b in bk)
        cands.append((hit, M, hex(T), hex(A), Nb, s, hit == M and s == M))
cands.sort(reverse=True)
for c in cands[:10]:
    print('命中%d/%s  M=%s T=%s A=%s 桶数=%s 桶条数和=%s 全自洽=%s' %
          (c[0], c[1], c[1], c[2], c[3], c[4], c[5], c[6]))

# 取最优解，检查桶表起始地址是否等于数组地址
hit, M, T, A, Nb, s, ok = cands[0]
T = int(T, 16); A = int(A, 16)
ents = parse_from(T)
byT = {e[0] + 4: e for e in ents}
arr = [struct.unpack_from('<I', raw, A + i * 4)[0] for i in range(M)]
bk = [struct.unpack_from('<II', raw, 0x08 + i * 8) for i in range(Nb)]
cum, k = [], 0
for off, ln in bk:
    cum.append(k); k += ln
print('\n桶表 off vs 数组地址(A+4*cum):', [(hex(b[0]), hex(A + 4 * c)) for b, c in list(zip(bk, cum))[:6]])
print('差值集合:', set(b[0] - (A + 4 * c) for b, c in zip(bk, cum)))
print('数组顺序的 hash 单调?', end=' ')
hs = [byT[a][1] for a in arr if a in byT]
print(all(hs[i] < hs[i+1] for i in range(len(hs) - 1)), ' (降序:',
      all(hs[i] > hs[i+1] for i in range(len(hs) - 1)), ')')
print('条目数 M =', M, ' 头部 0..A 大小', hex(A))
