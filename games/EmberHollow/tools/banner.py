"""Compose repository artwork from actual simulator screenshots.

Run the smoke recording first, then pass an output PNG path. No game pixels
are redrawn or synthesized; nearest-neighbour scaling preserves the art.
"""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    game=Path(__file__).resolve().parents[1]
    smoke=game/'out/smoke'
    canvas=Image.new('RGB',(1280,432),'#17101f')
    draw=ImageDraw.Draw(canvas)
    def font(size,bold=False):
        return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)
    draw.rectangle((0,0,1279,4),fill='#fb9b34')
    draw.rectangle((0,427,1279,431),fill='#803e27')
    draw.rectangle((33,49,366,382),fill='#544353')
    title=Image.open(smoke/'01_title.png').convert('RGB').resize((320,320),Image.Resampling.NEAREST)
    canvas.paste(title,(40,56))
    draw.text((409,38),'EMBER HOLLOW',font=font(44,True),fill='#ffeb91')
    draw.text((412,98),'SIX LANTERNS. ONE LAST SPARK.',font=font(20,True),fill='#fb9b34')
    draw.text((412,131),'A Halloween adventure for CHGame Rev0 / WeAct F8U6',font=font(16),fill='#c8bbc8')
    panels=[('02_story_one.png','THE CURSE AWAKENS'),('06_warden.png','FACE THE ASH WARDEN'),('08_victory.png','BRING THE DAWN HOME')]
    for x,(filename,label) in zip((412,690,968),panels):
        draw.rectangle((x-3,176,x+195,374),fill='#544353')
        frame=Image.open(smoke/filename).convert('RGB').resize((192,192),Image.Resampling.NEAREST)
        canvas.paste(frame,(x,179))
        draw.text((x,387),label,font=font(13,True),fill='#ffeb91')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(args.output,optimize=True)
    print(args.output)
if __name__=='__main__':main()
