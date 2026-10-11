"""Publish the checked simulator clips as five beginner GIFs."""
from pathlib import Path
import shutil
from PIL import Image
GAME=Path(__file__).resolve().parents[1]
def main():
    target=GAME/'docs/tutorials';target.mkdir(parents=True,exist_ok=True)
    for stem in ('01_parry','02_bridge_map','03_boss_dodge','04_victory','05_retry'):
        source=GAME/'out/tutorials'/f'{stem}.gif'
        with Image.open(source) as im:
            if im.n_frames<2 or im.size!=(384,384):raise ValueError(f'Bad clip: {source}')
            for n in range(im.n_frames):im.seek(n);im.load()
        if source.stat().st_size>1_000_000:raise ValueError(f'Clip too large: {source}')
        shutil.copyfile(source,target/f'{stem[3:]}.gif')
        print(f'{stem[3:]}.gif: {source.stat().st_size:,} bytes')
if __name__=='__main__':main()
