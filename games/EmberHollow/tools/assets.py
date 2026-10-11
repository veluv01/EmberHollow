"""Original 16-colour pixel art and the fixed world; regenerate Assets.cpp.

All shapes are drawn at their native pixel size. No purchased sprite sheets,
neural image assets, or runtime files are needed. Pillow is the only dependency.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
GAME = HERE.parent
COLOURS = ["#101018", "#241b30", "#362538", "#524052", "#765766", "#39222a",
           "#752e2a", "#a64925", "#e8762c", "#ffae38", "#ffe071", "#b9af9e",
           "#eae1c1", "#679483", "#455775", "#be5653"]


def canvas(w, h, bg=0):
    im = Image.new("P", (w, h), bg)
    palette = [int(c[i:i+2], 16) for c in COLOURS for i in (1, 3, 5)]
    im.putpalette(palette + [0] * (768-len(palette)))
    return im, ImageDraw.Draw(im)


def pumpkin(d, x, y, size=1, face=True):
    # Native small octagon; body ramp catches light from the upper left.
    d.polygon([(x+2,y),(x+7,y),(x+9,y+2),(x+9,y+6),(x+7,y+8),
               (x+2,y+8),(x,y+6),(x,y+2)], fill=6)
    d.rectangle((x+1,y+2,x+7,y+6),fill=8)
    d.rectangle((x+3,y+1,x+5,y+7),fill=9)
    d.line((x+2,y+3,x+2,y+5),fill=7)
    d.line((x+6,y+2,x+6,y+6),fill=7)
    d.rectangle((x+4,y-2,x+5,y),fill=13)
    if face:
        d.point((x+2,y+3),fill=0);d.point((x+6,y+3),fill=0)
        d.line((x+3,y+6,x+6,y+6),fill=0);d.point((x+4,y+5),fill=0)


def hero(direction, step):
    im,d=canvas(14,18)
    d.line((3,16-step,5,16-step),fill=0,width=2)
    d.line((9,16-(1-step),11,16-(1-step)),fill=0,width=2)
    d.polygon([(3,8),(10,8),(12,14),(1,14)],fill=0)
    d.polygon([(4,9),(9,9),(10,13),(3,13)],fill=14)
    d.rectangle((4,9,6,12),fill=13)
    d.line((3,13,10,13),fill=3)
    d.rectangle((3,14,5,15),fill=4);d.rectangle((9,14,10,15),fill=3)
    pumpkin(d,2,2,face=direction!=2)
    if direction in (1,3):
        d.rectangle((2,4,4,7),fill=8)
        d.point((8,5),fill=0);d.line((8,8,10,8),fill=0)
        d.rectangle((1,10,2,13),fill=4)
        d.rectangle((11,9,12,12),fill=11);d.point((12,9),fill=12)
        if direction==1: im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    else:
        d.rectangle((1,10,2,12),fill=11);d.rectangle((11,10,12,12),fill=4)
        if direction==2:
            d.rectangle((4,10,9,13),fill=14);d.line((4,9,8,9),fill=13)
    return im


def skeleton(step):
    im,d=canvas(14,18)
    d.polygon([(4,1),(9,1),(11,3),(11,7),(9,9),(4,9),(2,7),(2,3)],fill=0)
    d.rectangle((4,2,9,7),fill=11);d.rectangle((4,2,8,4),fill=12)
    d.rectangle((4,4,5,5),fill=0);d.rectangle((8,4,9,5),fill=0)
    d.point((7,6),fill=0);d.line((5,8,9,8),fill=12)
    d.line((6,9,6,13),fill=11);d.line((4,10,9,10),fill=12)
    d.line((4,12,9,12),fill=11);d.line((3,10,1,13-step),fill=11)
    d.line((10,10,12,12+step),fill=12)
    d.line((5,14,3,16-step),fill=11);d.line((8,14,10,16-(1-step)),fill=12)
    d.line((2,17-step,4,17-step),fill=11);d.line((9,17-(1-step),11,17-(1-step)),fill=11)
    return im


def bat(step):
    im,d=canvas(18,12)
    if step:
        d.polygon([(1,1),(6,5),(8,4),(10,4),(12,5),(16,1),(17,7),(13,6),
                   (12,9),(10,8),(8,8),(6,9),(4,6),(0,7)],fill=3)
        d.line((1,2,5,6),fill=4);d.line((13,6,16,2),fill=4)
    else:
        d.polygon([(0,5),(5,3),(7,5),(11,5),(13,3),(17,5),(15,9),(12,8),
                   (11,10),(7,10),(6,8),(3,9)],fill=3)
        d.line((1,5,5,4),fill=4);d.line((13,4,16,5),fill=4)
    d.polygon([(6,2),(8,4),(10,4),(12,2),(12,8),(9,10),(6,8)],fill=0)
    d.rectangle((7,5,11,8),fill=2);d.point((7,6),fill=15);d.point((11,6),fill=15)
    return im


def slime(step):
    im,d=canvas(16,12)
    yy=1 if step else 3
    d.polygon([(3,yy+2),(6,yy),(10,yy),(13,yy+2),(15,9),(13,11),(2,11),(0,9)],fill=6)
    d.polygon([(4,yy+2),(7,yy+1),(10,yy+1),(12,yy+3),(13,9),(3,9)],fill=8)
    d.line((5,yy+3,9,yy+2),fill=9,width=2)
    d.point((6,yy+4),fill=0);d.point((10,yy+4),fill=0)
    d.line((6,yy+6,10,yy+6),fill=7)
    return im


def shrine(live):
    im,d=canvas(20,24)
    d.polygon([(2,18),(5,16),(14,16),(18,19),(18,22),(1,22)],fill=0)
    d.rectangle((3,18,16,20),fill=3);d.line((4,18,15,18),fill=4)
    d.rectangle((6,8,13,17),fill=2);d.line((6,8,6,16),fill=4)
    d.rectangle((7,9,12,10),fill=3)
    if live:
        pumpkin(d,5,4)
        d.polygon([(2,11),(4,6),(3,12),(5,14),(3,17),(1,15)],fill=8)
        d.polygon([(16,10),(18,6),(17,12),(19,14),(17,17),(15,14)],fill=8)
        d.point((2,13),fill=10);d.point((17,14),fill=9)
        d.line((8,12,11,15),fill=9);d.line((11,12,8,15),fill=9)
    else:
        d.line((7,11,12,15),fill=0,width=2)
        d.rectangle((7,5,12,8),fill=13);d.point((9,4),fill=12)
        d.line((9,9,9,12),fill=13)
    return im


def home():
    im,d=canvas(32,30)
    d.polygon([(1,12),(13,1),(18,1),(30,12),(29,16),(2,16)],fill=0)
    d.polygon([(4,12),(14,3),(18,3),(27,12)],fill=3)
    d.line((6,11,14,4),fill=4,width=2)
    for y in (9,12): d.line((10,y,24,y),fill=2)
    d.rectangle((5,15,26,27),fill=2);d.line((5,15,24,15),fill=4)
    d.rectangle((12,18,19,28),fill=0);d.rectangle((13,19,18,27),fill=7)
    d.rectangle((7,18,9,21),fill=9);d.rectangle((22,18,24,21),fill=9)
    d.line((3,28,29,28),fill=4)
    pumpkin(d,0,20);pumpkin(d,23,21)
    return im


def boss(step):
    im,d=canvas(34,38)
    d.line((7,34-step,12,35-step),fill=0,width=3)
    d.line((23,35-(1-step),29,34-(1-step)),fill=0,width=3)
    d.polygon([(7,20),(11,15),(23,15),(28,20),(30,32),(24,35),(8,35),(3,31)],fill=0)
    d.polygon([(10,18),(23,18),(26,22),(28,30),(22,32),(8,31),(7,23)],fill=3)
    d.polygon([(10,20),(15,18),(15,29),(8,29)],fill=4)
    d.rectangle((15,22,24,24),fill=2)
    d.polygon([(4,21),(8,19),(11,25),(6,30),(1,27)],fill=6)
    d.polygon([(26,19),(30,20),(33,27),(28,30),(24,25)],fill=6)
    d.line((3,23,7,21),fill=8,width=2);d.line((27,22,30,24),fill=8,width=2)
    d.polygon([(9,4),(14,1),(21,2),(27,6),(28,14),(24,20),(12,21),(6,16),(5,9)],fill=6)
    d.polygon([(10,5),(14,3),(20,4),(25,7),(25,14),(22,18),(13,19),(8,14),(8,8)],fill=8)
    d.line((13,4,12,11,13,17),fill=9,width=2)
    d.line((20,5,22,11,20,17),fill=7,width=2)
    d.polygon([(8,8),(14,10),(9,12)],fill=0);d.polygon([(23,8),(18,10),(23,12)],fill=0)
    d.line((10,10,12,10),fill=10);d.line((20,10,22,10),fill=10)
    d.polygon([(10,15),(14,14),(16,16),(19,14),(23,15),(20,18),(13,18)],fill=0)
    d.line((12,16,14,16),fill=10);d.line((19,16,21,16),fill=10)
    d.polygon([(5,9),(2,2),(7,5),(9,1),(10,6)],fill=4)
    d.polygon([(24,5),(27,1),(27,5),(31,2),(28,10)],fill=4)
    d.polygon([(15,1),(17,0),(18,3)],fill=13)
    d.rectangle((14,26,20,29),fill=6);d.line((15,27,19,27),fill=9)
    return im


def tiles():
    output=[]
    for k in range(12):
        im,d=canvas(8,8,1 if k in (0,4,5,6,10,11) else 0)
        if k in (0,10,11):
            if k==0: d.line((1,6,3,6),fill=2);d.line((6,1,7,1),fill=2)
            if k==10:d.line((0,4,3,3),fill=2);d.line((3,3,5,3),fill=2)
            if k==11:d.polygon([(1,2),(4,2),(5,3),(2,4)],fill=2)
        elif k==1:
            d.rectangle((0,0,7,7),fill=2);d.line((0,0,7,0),fill=4)
            d.line((0,1,0,6),fill=3);d.line((4,1,4,3),fill=0)
            d.line((0,4,7,4),fill=0);d.line((2,5,2,7),fill=0)
            d.line((5,2,7,2),fill=3)
        elif k in (2,8,9):
            d.rectangle((0,0,7,7),fill=7)
            off={2:0,8:2,9:4}[k]
            for y in (1,4,7):
                x=(y*3+off)%8;d.line((x-2,y,x+2,y),fill=8)
                d.line((x,y+1,x+2,y+1),fill=9)
            d.line((2,(off+2)%8,4,(off+2)%8),fill=6)
        elif k==3:
            d.rectangle((0,0,7,7),fill=5)
            for y in (0,3,6):d.line((0,y,7,y),fill=7);d.line((0,y+1,7,y+1),fill=6)
            d.line((1,0,1,7),fill=4);d.line((6,0,6,7),fill=3)
        elif k==4:
            d.polygon([(2,2),(4,1),(6,2),(6,6),(1,6),(1,3)],fill=3)
            d.line((2,2,4,2),fill=4);d.line((3,3,3,5),fill=2);d.line((2,4,4,4),fill=2)
        elif k==5:
            d.polygon([(2,2),(5,2),(7,4),(6,6),(1,6),(0,4)],fill=7)
            d.rectangle((2,3,5,5),fill=8);d.line((3,3,3,5),fill=9);d.point((4,1),fill=13)
        elif k==6:
            d.line((1,2,5,5),fill=11);d.point((1,3),fill=11);d.point((5,4),fill=11)
        elif k==7:
            d.rectangle((0,0,7,7),fill=0)
            d.line((1,0,1,7),fill=6,width=2);d.line((6,0,6,7),fill=6,width=2)
            d.line((0,2,7,2),fill=8);d.line((0,6,7,6),fill=7)
        output.append(im)
    return output


def world():
    w,h=64,48
    grid=[[0]*w for _ in range(h)]
    def rect(x0,y0,x1,y1,t):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):grid[y][x]=t
    rect(0,0,63,0,1);rect(0,47,63,47,1);rect(0,0,0,47,1);rect(63,0,63,47,1)
    # Two rivers divide three districts, with deliberately wide crossings.
    rect(19,12,21,46,2);rect(18,20,22,22,3);rect(18,36,22,38,3)
    rect(22,27,62,29,2);rect(31,26,34,30,3);rect(47,26,50,30,3)
    rect(2,5,17,9,2);rect(6,5,9,9,3)
    # Warden's island and its sealed southern entrance.
    rect(47,1,61,12,1);rect(48,2,60,11,2);rect(49,3,59,10,0)
    rect(52,10,55,13,3);rect(52,12,55,12,7)
    # Basalt ridges leave routes above/below and through a small doorway.
    rect(4,25,8,26,1);rect(14,12,17,14,1);rect(25,16,27,18,1)
    rect(36,34,39,36,1);rect(54,34,57,38,1);rect(38,7,42,10,1)
    rect(28,40,36,41,1);rect(38,24,42,25,1)
    for x,y in [(5,18),(7,18),(9,18),(5,21),(7,21),(15,21),(27,34),(29,34),
                (41,17),(43,18),(46,19),(53,21),(56,23),(49,39),(51,40),(54,42)]:grid[y][x]=4
    for x,y in [(4,34),(6,35),(5,37),(8,42),(10,42),(14,39),(25,44),(27,43),
                (40,31),(42,32),(45,37),(48,33),(56,15),(57,17),(33,13)]:grid[y][x]=5
    for x,y in [(14,29),(16,31),(27,20),(34,36),(42,20),(48,23),(58,40)]:grid[y][x]=6
    # Every encounter/pickup has a walkable footprint.
    for px,py in [(68,316),(100,276),(196,300),(100,164),(260,188),(364,276),(356,140),
                  (76,284),(116,212),(180,276),(244,204),(308,180),(380,252),(380,124),(436,84)]:
        tx,ty=px//8,py//8
        for yy in range(ty-1,ty+2):
            for xx in range(tx-1,tx+2):grid[yy][xx]=0
    return grid


def word_mask(word):
    # A native 9x13 stroke alphabet, with octagonal O/B curves and clipped ends.
    mask=Image.new("L",(len(word)*11-1,15));d=ImageDraw.Draw(mask)
    for i,ch in enumerate(word):
        x=i*11+1
        def line(points):d.line([(x+a,b+1) for a,b in points],fill=255,width=2)
        if ch=="E":line([(8,0),(0,0),(0,12),(8,12)]);line([(0,6),(6,6)])
        elif ch=="M":line([(0,12),(0,0),(4,5),(8,0),(8,12)])
        elif ch=="B":line([(0,12),(0,0),(6,0),(8,2),(8,4),(6,6),(0,6)]);line([(6,6),(8,8),(8,10),(6,12),(0,12)])
        elif ch=="R":line([(0,12),(0,0),(6,0),(8,2),(8,4),(6,6),(0,6)]);line([(4,6),(8,12)])
        elif ch=="H":line([(0,0),(0,12)]);line([(8,0),(8,12)]);line([(0,6),(8,6)])
        elif ch=="O":line([(2,0),(6,0),(8,2),(8,10),(6,12),(2,12),(0,10),(0,2),(2,0)])
        elif ch=="L":line([(0,0),(0,12),(8,12)])
        elif ch=="W":line([(0,0),(0,12),(4,8),(8,12),(8,0)])
    return mask


def title_scene():
    im,d=canvas(128,128)
    # Cooler sky, distant ruined spires, and a cut-out crescent moon.
    d.rectangle((1,1,126,82),fill=1)
    d.polygon([(1,69),(7,58),(11,61),(14,49),(18,56),(22,67),(29,64),(37,73),(42,57),
               (45,54),(46,67),(55,72),(63,64),(70,73),(79,65),(87,66),(94,49),
               (96,43),(99,49),(101,61),(110,63),(118,56),(126,66),(126,87),(1,87)],fill=2)
    d.ellipse((91,7,118,34),fill=11);d.ellipse((84,3,112,31),fill=1)
    d.line((102,31,112,25),fill=12)
    for x,y in [(8,8),(20,16),(77,11),(87,39),(117,44),(12,41)]:d.point((x,y),fill=4)
    # A diagonal lava chasm, with basalt shelves and warm rims.
    d.polygon([(2,96),(24,86),(40,89),(54,78),(76,85),(87,75),(125,83),(126,126),(1,126)],fill=6)
    d.polygon([(1,109),(27,96),(44,103),(62,91),(81,100),(101,88),(125,97),(125,125),(1,125)],fill=7)
    for points,c in [([(3,112),(28,102),(48,111),(66,100),(85,109),(111,98),(125,104)],8),
                     ([(7,121),(29,112),(46,118),(66,110),(87,117),(107,107),(121,112)],9),
                     ([(2,124),(22,120),(40,123)],8)]:d.line(points,fill=c,width=2)
    d.polygon([(11,87),(37,78),(65,83),(75,92),(61,104),(27,105),(8,98)],fill=0)
    d.polygon([(12,87),(38,79),(65,84),(70,91),(59,98),(28,99),(11,95)],fill=3)
    d.line((12,87,38,79,64,84),fill=4,width=2)
    d.polygon([(92,69),(123,71),(126,83),(117,91),(88,85),(81,78)],fill=0)
    d.line((93,70,121,72),fill=4,width=2)
    # A bespoke larger guardian portrait, drawn at this size (not a scaled sprite).
    d.polygon([(39,76),(46,60),(64,62),(73,78),(70,94),(35,93)],fill=0)
    d.polygon([(45,68),(62,66),(68,80),(65,90),(39,89)],fill=14)
    d.polygon([(45,69),(51,66),(52,84),(42,88)],fill=13)
    d.polygon([(43,40),(59,37),(69,44),(72,57),(66,67),(47,70),(36,61),(35,49)],fill=6)
    d.polygon([(45,42),(58,40),(66,46),(68,56),(62,64),(48,66),(39,59),(39,49)],fill=8)
    d.line((49,41,45,51,47,64),fill=9,width=2)
    d.line((59,42,62,53,59,64),fill=7,width=2)
    d.polygon([(42,50),(50,53),(44,56)],fill=0);d.polygon([(62,49),(56,53),(62,55)],fill=0)
    d.line((45,53,48,53),fill=10);d.line((58,52,61,52),fill=10)
    d.polygon([(45,60),(51,58),(54,61),(60,58),(63,60),(58,64),(49,64)],fill=0)
    d.polygon([(51,38),(54,33),(59,34),(57,38)],fill=13)
    d.polygon([(34,69),(28,72),(28,84),(36,87),(41,80)],fill=3)
    d.line((29,74,33,71),fill=11,width=2)
    # Sword gleams against the moon-side darkness.
    d.polygon([(68,72),(91,46),(94,43),(92,49),(74,78)],fill=0)
    d.line((72,73,92,46),fill=11,width=3);d.line((73,71,92,45),fill=12)
    d.line((66,72,77,80),fill=9,width=2);d.line((65,79,68,76),fill=4,width=3)
    pumpkin(d,13,86);pumpkin(d,101,78)
    # Title is its own native lettering. Tiny outline/extrusion, warm face.
    for word,y in [("EMBER",3),("HOLLOW",20)]:
        mask=word_mask(word);x=(128-mask.width)//2
        edge=mask.filter(ImageFilter.MaxFilter(3))
        im.paste(0,(x+1,y+2),edge);im.paste(6,(x+1,y+1),mask);im.paste(10,(x,y),mask)
        # Darker lower faces, without antialiasing.
        for yy in range(9,mask.height):
            for xx in range(mask.width):
                if mask.getpixel((xx,yy)):im.putpixel((x+xx,y+yy),9)
    # Calm bottom band for the game's Continue/New selector.
    d.rectangle((12,107,115,124),fill=0);d.line((18,106,109,106),fill=6)
    return im


def pack(im):
    b=bytearray()
    for y in range(im.height):
        for x in range(0,im.width,2):
            b.append(im.getpixel((x,y)) | ((im.getpixel((x+1,y)) if x+1<im.width else 0)<<4))
    return bytes(b)


def array(name, data):
    rows=[", ".join(f"0x{v:02x}" for v in data[i:i+24]) for i in range(0,len(data),24)]
    return f"const uint8_t {name}[{len(data)}] = {{\n    "+",\n    ".join(rows)+"\n};\n"


def main():
    images=[hero(0,0),hero(0,1),hero(2,0),hero(2,1),hero(3,0),hero(3,1),hero(1,0),hero(1,1),
            skeleton(0),skeleton(1),bat(0),bat(1),slime(0),slime(1),shrine(True),shrine(False)]
    candy,d=canvas(12,10);d.polygon([(0,3),(3,1),(3,3),(8,3),(9,1),(11,3),(11,7),(9,9),(8,7),(3,7),(3,9),(0,7)],fill=13)
    d.rectangle((4,3,7,6),fill=12);images += [candy,home(),boss(0),boss(1)]
    ts=tiles();terrain=world();scene=title_scene()
    palette=[((int(c[1:3],16)>>3)<<11)|((int(c[3:5],16)>>2)<<5)|(int(c[5:7],16)>>3) for c in COLOURS]
    text='// Generated by tools/assets.py. Edit the recipe, not these bytes.\n#include "Assets.h"\nnamespace eh { namespace assets {\n'
    text += 'const uint16_t Palette[16] = {'+', '.join(f'0x{x:04x}' for x in palette)+'};\n'
    text += array('World',bytes(t for row in terrain for t in row))
    text += 'const uint8_t Tiles[12][32] = {\n'+',\n'.join('    {'+', '.join(f'0x{x:02x}' for x in pack(t))+'}' for t in ts)+'\n};\n'
    text += array('TitleScene',pack(scene))
    for i,im in enumerate(images):text += array(f'Sprite{i}',pack(im))
    text += 'const Sprite Sprites[SpriteCount] = {\n'+',\n'.join(f'    {{Sprite{i}, {im.width}, {im.height}}}' for i,im in enumerate(images))+'\n};\n} }\n'
    (GAME/'src/assets/Assets.cpp').write_text(text,encoding='utf-8',newline='\n')
    out=GAME/'docs';out.mkdir(exist_ok=True)
    scene.convert('RGB').save(out/'title.png')
    sheet=Image.new('RGB',(160,96),COLOURS[1])
    for i,im in enumerate(images):sheet.paste(im.convert('RGB'),((i%5)*32,(i//5)*24))
    sheet.save(out/'sprites.png')
    mapim=Image.new('RGB',(512,384))
    for y,row in enumerate(terrain):
        for x,t in enumerate(row):mapim.paste(ts[t].convert('RGB'),(x*8,y*8))
    mapim.save(out/'world.png')
    print(f'Generated {len(images)} sprites, 12 tiles, a 64x48 world and a 128x128 title.')


if __name__=='__main__':main()

