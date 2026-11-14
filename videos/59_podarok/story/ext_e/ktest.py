import os, sys, subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(os.path.dirname(HERE),"common"))
import lib, kitchen
os.makedirs("/tmp/e59",exist_ok=True)
for k in (0,.5,1):
    lib.DEFS.clear()
    st=kitchen.static(); lg,top=kitchen.table(-100,600)
    body=f'<g transform="{lib.cam(560,1000,1.2,0)}">{st}{kitchen.oven_glow(k,0)}{lg}{top}{kitchen.oven_door(k)}</g>'
    open(f"/tmp/e59/k{k}.svg","w").write(lib.svg(body))
open("/tmp/e59/list.txt","w").write("\n".join(f"/tmp/e59/k{k}.svg\t/tmp/e59/k{k}.png" for k in (0,.5,1)))
subprocess.check_call(["node",os.path.join(HERE,"render.js"),"/tmp/e59/list.txt","png","1","x"])
