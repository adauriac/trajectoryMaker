import random
import sys

width=800
height=600
scaler = 0.1
N=int(sys.argv[1])

xcur=width/2
ycur=height/2
f=open("./rndTraj%d"%N,'w')
for i in range(N):
    while True:
        dx = (random.random()-0.5)*width*scaler
        x = xcur+dx
        dy = (random.random()-0.5)*height*scaler
        y = ycur+dy
        if x>=0 and  x<=width and y>=0 and y<= height:
            break
    xcur = x
    ycur = y
    p = 0 if random.random()<0.5 else 1
    st = f"type=line xF={int(xcur)} yF={int(ycur)} zF=0 speed=1 plasma={p}\n"
    print(st,end="")
    f.writelines(st)
f.close()
