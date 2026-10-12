"""Import the pinned, unmodified CHGame dependency; build/check with PlatformIO."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT/'games/EmberHollow'
SKIP={'.git','.pio','build','out','__pycache__'}
OWN_TOOLS={'project.py','requirements.txt'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command,log=None,env=None):
    print('+ '+' '.join(map(str,command)),flush=True)
    if log is None:
        subprocess.run(list(map(str,command)),cwd=ROOT,env=env,check=True);return
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf-8') as record:
        p=subprocess.Popen(list(map(str,command)),cwd=ROOT,env=env,stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        for line in p.stdout:print(line,end='',flush=True);record.write(line)
        if p.wait():raise SystemExit(f'Command failed; see {log}')

def setup(source=None):
    lock=json.loads((ROOT/'dependency-lock.json').read_text())['chgame']
    deps=ROOT/'.deps';deps.mkdir(exist_ok=True)
    if source is None:
        source=deps/'CHGame'
        if not source.exists():run(['git','clone','--no-checkout',lock['repository'],source])
        status=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
        head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        initialized=(source/'platform/board/arduino/CHGame/boards.txt').exists()
        if initialized and status:raise SystemExit('Dependency clone has local edits; preserve them before setup.')
        if not initialized or head!=lock['revision']:
            run(['git','-C',source,'fetch','origin',lock['revision']])
            run(['git','-C',source,'checkout','--detach',lock['revision']])
    else:
        source=source.resolve()
        print('Using the supplied CHGame checkout; its revision is not enforced.')
    required=('platform/board/arduino/CHGame/boards.txt','ports/weact-f8u6/environments.ini','tools/chgame.py')
    if not all((source/item).is_file() for item in required):raise SystemExit('Incomplete CHGame / WeAct dependency.')
    manifest=deps/'imported-files.json'
    previous=json.loads(manifest.read_text()) if manifest.exists() else {}
    entries={}
    for folder in ('platform','ports','tools','spec'):
        for item in sorted((source/folder).rglob('*')):
            relative=item.relative_to(source)
            if not item.is_file() or any(p in SKIP for p in relative.parts):continue
            if folder=='tools' and len(relative.parts)==2 and item.name in OWN_TOOLS:continue
            entries[relative.as_posix()]=(item,digest(item))
    for relative,(_,sha) in entries.items():
        target=ROOT/relative
        if target.exists() and digest(target) not in {sha,previous.get(relative)}:
            raise SystemExit(f'Local change preserved: {relative}. Move it aside before setup.')
    obsolete=[]
    for relative,sha in previous.items():
        if relative not in entries and (ROOT/relative).is_file():
            if digest(ROOT/relative)!=sha:raise SystemExit(f'Local change preserved: {relative}')
            obsolete.append(ROOT/relative)
    for relative,(item,sha) in entries.items():
        target=ROOT/relative
        if not target.exists() or digest(target)!=sha:
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(item,target)
    for item in obsolete:item.unlink()
    manifest.write_text(json.dumps({key:sha for key,(_,sha) in entries.items()},indent=2)+'\n')
    print(f'Ready: {len(entries)} unmodified dependency files. Open the repository root in PlatformIO.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=('setup','build','check','gifs'))
    ap.add_argument('--source',type=Path,help='Use an existing checkout without modifying it')
    args=ap.parse_args();setup(args.source)
    if args.action=='setup':return
    if args.action=='build':
        run([sys.executable,'-m','platformio','run','-e','ember','-e','ember-debug','-e','ember-rev0','-e','ember-rev0-debug'],ROOT/'out/build.log')
    else:
        env=dict(os.environ)
        if os.name!='nt':
            env.setdefault('CHSIM_CXX','g++');env.setdefault('CHSIM_FLAGS','-include chrono')
        if args.action=='check':
            run([sys.executable,ROOT/'tools/chgame.py','--sketch',GAME,'check','--no-device'],ROOT/'out/check.log',env)
        else:
            run([sys.executable,ROOT/'tools/readme_gif.py',GAME],env=env)
            run([sys.executable,GAME/'tools/chsim/chdrive.py','--sim',GAME,GAME/'tools/scripts/tutorials.txt',GAME/'out/tutorials'],env=env)
            run([sys.executable,GAME/'tools/tutorial_gifs.py'],env=env)
if __name__=='__main__':main()
