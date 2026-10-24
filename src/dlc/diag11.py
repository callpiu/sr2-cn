# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()
N = len(raw)

def parse_from(T):
    o = T; ents = []
    while o + 4 <= N:
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= N:
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        ents.append((o - 4, h, ''.join(chr(c) for c in cps)))
    return (ents, o == N)

for T in (0x1330, 0x132C, 0x1334):
    ents, ok = parse_from(T)
    M = len(ents)
    print('T=0x%X 条目=%d 到文件尾=%s' % (T, M, ok), end='  ')
    if not ok:
        print()
        continue
    byT = {e[0] + 4: e for e in ents}
    for Nb in range(115, 135):
        A = 8 + Nb * 8
        if A + 4 * (M) > T:
            continue
        arr = [struct.unpack_from('<I', raw, A + i * 4)[0] for i in range(M)]
        hit = sum(1 for a in arr if a in byT)
        bk = [struct.unpack_from('<II', raw, 8 + i * 8) for i in range(Nb)]
        s = sum(b[1] for b in bk)
        if hit == M and s == M:
            print('★ A=0x%X 桶数=%d 指针命中=%d/%d 桶条数和=%d' % (A, Nb, hit, M, s))
            # 桶 off 与数组地址关系
            cum, k = [], 0
            for off, ln in bk:
                cum.append(k); k += ln
            d = set(b[0] - (A + 4 * c) for b, c in zip(bk, cum))
            print('   off-(A+4*cum) 取值集合:', sorted(d)[:6], '...共', len(d))
            d2 = set(b[0] - (A + 4 * (c + b[1])) for b, c in zip(bk, cum))
            print('   off-(A+4*(cum+count)):', sorted(d2)[:6], '...共', len(d2))
    print()
