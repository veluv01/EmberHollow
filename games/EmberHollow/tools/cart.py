"""Ember Hollow's 128x128 visual-menu cover, using CHGame's artkit.

The native pixel scene and lettering are original tools/assets.py recipes.
This pass maps them to the menu's reserved colours and 11 own colours.
"""
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
for parent in HERE.parents:
    if (parent/'tools/artkit').is_dir():
        sys.path.insert(0,str(parent/'tools'))
        break
else:
    raise SystemExit('Run this recipe inside a CHGame checkout.')
import artkit as ak
sys.path.insert(0,str(HERE))
from assets import title_scene


def draw():
    palette=ak.Palette({
        'night':'#241b30','purple':'#362538','stone':'#524052','rim':'#765766',
        'ember0':'#752e2a','ember1':'#a64925','ember2':'#e8762c',
        'gold0':'#ffae38','gold1':'#ffe071','sage':'#679483','cloak':'#455775'},
        ramps=[['black','night','purple','stone','rim'],
               ['black','ember0','ember1','ember2','gold0','gold1','cream']])
    rgb=np.asarray(title_scene().convert('RGB'),dtype=np.float32)/255.0
    cv=ak.Canvas(ss=1)
    cv.rgb[:]=rgb
    cv.dith[:]=0 # This is hand-clustered pixel art: preserve its clean edges.
    picture=cv.quantize(palette)
    # The install bar occupies this empty band; keep all four edges dark.
    picture.idx[0,:]=palette['black'];picture.idx[-1,:]=palette['black']
    picture.idx[:,0]=palette['black'];picture.idx[:,-1]=palette['black']
    return picture.image()


if __name__=='__main__':
    import boxart
    out=HERE.parent/'docs/cart.png'
    boxart.save(draw(),out)
    print(out)

