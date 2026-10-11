"""Use the shared driver; say W/C/H/Z are the game fixtures (NOTES.md)."""
from pathlib import Path
import sys
for parent in Path(__file__).resolve().parents:
    if (parent/'tools/chsim/chdrivelib.py').is_file():
        sys.path.insert(0,str(parent/'tools/chsim'))
        break
else:
    raise SystemExit('The CHGame simulator tools were not found.')
from chdrivelib import main, Driver, to_image
from PIL import Image
IDENT='EHLO'

class EmberDriver(Driver):
    def op(self,name,args,outdir):
        # Shared recorder assumes 60 Hz; this game uses 30 Hz logic.
        if name=='rec' and args[0]=='stop':
            shots,self.rec=self.rec,None
            frames=[to_image(data,3) for data in shots]
            target=outdir/f'{args[1]}.gif'
            temporary=outdir/f'.{args[1]}.tmp'
            frames[0].save(temporary,format='GIF',save_all=True,append_images=frames[1:],
                           duration=round(1000*self.rec_every/30),loop=0)
            with Image.open(temporary) as check:
                for index in range(check.n_frames):check.seek(index);check.load()
            temporary.replace(target)
            print(f'{args[1]}.gif: {len(frames)} frames at 30 Hz logic',flush=True)
            return True
        return False

if __name__=='__main__':main(EmberDriver,ident=IDENT)

