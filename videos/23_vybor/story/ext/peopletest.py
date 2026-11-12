import sys, math
sys.path.insert(0, '.')
import lib
from person import draw
from jars import jar, JAMS
CAST = {
 "anna": dict(skin="#f2c9a8", hair="bob", hair_c="#c8622a", top="#4a8fc0", low="#2f3a5a", shoes="#5a3a2a", face=.5, collar="#f0ece0"),
 "oleg": dict(skin="#e8b896", hair="bald", hair_c="#9a9aa6", top="#7a8a4a", low="#4a4450", face=-.4, glasses=True, mustache=True, bw=1.12, zip=True),
 "kira": dict(skin="#8a5a3c", hair="curly", hair_c="#2a1a14", top="#e8a63a", low="#3a3a4a", face=.3, stripes="#f6e6c0", h=.95),
 "ivan": dict(skin="#f0c4a0", hair="short", hair_c="#e0b050", top="#c0403a", low="#3a4a6a", face=0.0, cap="#2a5a8a", stubble=True),
 "lena": dict(skin="#f4d0b4", hair="ponytail", hair_c="#3a2418", top="#8a5ab0", low="#2a2a3a", face=-.6, h=.97),
 "mira": dict(skin="#d9a07a", hair="bun", hair_c="#5a3020", top="#3a9a8a", low="#e8dcc0", face=.2, h=.93),
}
lib.lin_grad([(0,"#ffffff",1),(1,"#ffffff",1)], gid="gx")
lib.static_done(); lib.dyn_begin()
body = ['<rect width="1080" height="1920" fill="#f3efe4"/>']
t = float(sys.argv[1]) if len(sys.argv) > 1 else 0
for i,(k,sp) in enumerate(CAST.items()):
    x = 180 + (i%3)*360; y = 900 + (i//3)*850
    pose = {"walk": t*6 + i} if i in (0, 3) else {"arms": {"R": (150, 30)} if i == 2 else {}}
    if i == 1: pose["basket"] = "L"
    if i == 4: pose.update(item=("R", JAMS[2]), arms={"R": (-30, -80)}, mouth="smile")
    if i == 2: pose.update(brow=1, mouth="wavy", look=(-.5,-.6))
    body.append(draw(sp, pose, x, y, 1.0, sd=i*1000))
for i in range(6):
    body.append(jar(120 + i*90, 1880, JAMS[i*4], 1.0, i))
open(sys.argv[2], 'w').write(lib.svg("".join(body)))
