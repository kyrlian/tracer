#!/usr/bin/python3
import random
xmin=ymin=0
xmax=ymax=6

def draw(path):
  matrix=[]
  for i in range(ymax):
    row=[]
    for j in range(xmax):
      row.append(".")
    matrix.append(row)
  for idx, cell in enumerate(path):
    cx,cy=cell
    px=py=nx=ny=0
    if idx>1:
      previous=path[idx-1]
      px,py=previous
    if idx<len(path)-1:
      next=path[idx+1]
      nx,ny=next
    if nx==cx==px:
      s="║"
    elif ny==cy==py:
      s="═"
    elif (ny<cy and px<cx) or (py<cy and nx<cx):
      s="╝"
    elif (ny>cy and px<cx) or (py>cy and nx<cx):
      s="╗"
    elif (ny<cy and px>cx) or (py<cy and nx>cx):
      s="╚"
    elif (ny>cy and px>cx) or (py>cy and nx>cx):
      s="╔"
    else:
      s="o"
    row=matrix[cy]
    row[cx]=s
    matrix[cy]=row
  for row in matrix:
    print("".join(row))

from multiprocessing import Process, Value

def extend(path,n):
  if n.value != 0:
    return False 
  if len(path)==xmax*ymax:
    n.value=1
    draw(path)
    return True
  (cx,cy)=path[-1]
  processlist=[]
  for (dx,dy) in random.sample([(-1,0),(1,0),(0,-1),(0,1)],4):
    ncx=cx+dx
    ncy=cy+dy
    if ncx>=xmin and ncx<xmax and ncy>=ymin and ncy<ymax and (ncx,ncy) not in path:
      npath=path.copy()
      npath.append((ncx,ncy))
      p = Process(target=extend, args=(npath,n,)) 
      p.start()
      processlist.append(p)
  for p in processlist:
    p.join()
  return False

import time
if __name__ == '__main__':
  start = time.perf_counter()
  n = Value('i', 0)
  extend([(0,0)],n)
  end = time.perf_counter()
  print(f"Time {end - start:0.4f} seconds")

    