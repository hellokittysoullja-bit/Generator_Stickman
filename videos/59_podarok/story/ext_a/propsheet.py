import os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(os.path.dirname(HERE),"common"))
import lib, props
from lib import svg, blob, rect_pts
def frame():
    b=blob(rect_pts(0,0,1080,1920),"#FAF3E3")
    k=1.6
    y=330
    b+=props.pie(180,y,k,"whole")+props.pie(520,y,k,"crooked")+props.pie(860,y,k,"cut")
    y=640
    b+=props.cake(170,y,k,1.0,0.3)+props.bouquet(520,y,k)+props.jar_flowers(860,y,k)
    y=960
    b+=props.giftbox(180,y,k)+props.giftbox(500,y,k,lid=1.0)
    items="".join(props.item(n,640+i*30,y-20,k*0.9) for i,n in enumerate(("book","teddy")))
    b+=props.basket(850,y,k,items)
    y=1500
    for i,n in enumerate(props.ITEMS):
        b+=props.item(n,120+i*170,y,1.6)
    return svg(b)
if __name__=="__main__":
    open("/tmp/a59a/props.svg","w").write(frame())
