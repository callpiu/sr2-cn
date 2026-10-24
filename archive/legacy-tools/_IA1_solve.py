# -*- coding: utf-8 -*-
# 求引擎公式: j = (R0 + (i-A)//C)*65 + ((i-A)%C)
OBS = [(332,362),(371,336),(391,354),(422,967),(1035,410),
       (1190,2342),(1836,1784),(2296,2268),(2667,2656)]
NAME = {332:"们",371:"你",391:"保",422:"兄",1035:"弟",1190:"护",1836:"的",2296:"要",2667:"需"}

def score(A,C,R0):
    hit=0
    for i,j in OBS:
        if i < A: continue
        m=i-A
        r=R0+m//C; c=m%C
        if c>=65: return -1
        if r*65+c == j: hit+=1
    return hit

best=[]
for A in range(0, 400):
    for C in range(58, 72):
        for R0 in range(0, 6):
            s=score(A,C,R0)
            if s>=3: best.append((s,A,C,R0))
best.sort(reverse=True)
print("命中 >=3 的组合 (共 %d):" % len(best))
for s,A,C,R0 in best[:25]:
    print("   hit=%d  A=%-4d C=%-3d R0=%d" % (s,A,C,R0))

if not best:
    print("无 >=3；打印最佳:")
    allc=[]
    for A in range(0,400):
        for C in range(58,72):
            for R0 in range(0,6):
                allc.append((score(A,C,R0),A,C,R0))
    allc.sort(reverse=True)
    for x in allc[:10]: print("   hit=%d A=%d C=%d R0=%d" % x)

# 也试: 没有 R0 项，直接 j=(i-A)//C*65+((i-A)%C)
print("\n--- 试变体: j = ((i-A)//C)*65 + ((i-A)%C) + R0*65 ---")
def score2(A,C,R0):
    hit=0
    for i,j in OBS:
        if i<A: continue
        m=i-A
        c=m%C
        if c>=65: return -1
        if (m//C)*65+c+R0*65 == j: hit+=1
    return hit
b2=[]
for A in range(0,400):
    for C in range(58,72):
        for R0 in range(0,3):
            s=score2(A,C,R0)
            if s>=3: b2.append((s,A,C,R0))
b2.sort(reverse=True)
for s,A,C,R0 in b2[:10]: print("   hit=%d A=%d C=%d R0=%d" % (s,A,C,R0))
