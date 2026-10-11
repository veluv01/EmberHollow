"""Check the actual CHGame flash record through the sketch's debug protocol."""
from pathlib import Path
import sys

GAME=Path(__file__).resolve().parents[2]
for parent in GAME.parents:
    if (parent/'tools/chsim/simsave.py').is_file():
        sys.path.insert(0,str(parent/'tools/chsim'))
        break
else:raise SystemExit('Run inside a CHGame checkout.')
from simsave import Session


def state(session):
    line=session.say('Z')
    return {key:int(value) for key,value in (field.split('=') for field in line.split()[1:])}


def main():
    s=Session(GAME)
    s.tap('A');s.check(state(s)['mode']==5,'NEW opens the story')
    s.frames(90);s.check(state(s)['ticks']==0,'story stops the quest clock')
    s.tap('B');s.say('C 5');s.say('W 268 188 2');s.say('H 4');s.frames(12)
    s.tap('START');before=state(s)
    s.check(before['mode']==2,'pause shows the map')
    s.frames(60);s.check(state(s)['ticks']==before['ticks'],'pause stops the game clock')
    s.power_cycle(settle=2);s.check(state(s)['mode']==0,'restart returns to title')
    s.tap('A');after=state(s)
    s.check(after['mode']==1,'CONTINUE bypasses the story')
    s.check(after['cleared']==5,'flash record retains the two cleared shrines')
    s.check((after['x'],after['y'])==(268,188),'flash record retains checkpoint position')
    s.check(after['hp']==4,'flash record retains checkpoint health')
    s.check(before['ticks']<=after['ticks']<=before['ticks']+5,'flash record retains elapsed game time')
    s.tap('START');s.power_cycle(settle=2);s.tap('RIGHT');s.tap('A')
    s.check(state(s)['mode']==5,'NEW shows the story again')
    s.check(state(s)['cleared']==5,'opening story does not overwrite the previous save')
    s.tap('A');s.tap('A');s.tap('A')
    s.check(state(s)['cleared']==0,'NEW starts a fresh quest')
    s.check((state(s)['x'],state(s)['y'])==(68,316),'NEW starts at the hut')
    s.buttons(64);s.frames(2)
    for _ in range(1000):
        if state(s)['quit_ms']>=3100:break
        s.frames(10)
    else:raise AssertionError('Exit clock did not advance')
    s.check(s.d.t.p.poll() is None,'holding START for three seconds does not exit')
    s.buttons(0);s.frames(1);s.check(state(s)['quit_ms']==0,'release cancels the exit countdown')
    s.buttons(64);s.frames(1)
    for _ in range(2000):
        if state(s)['quit_ms']>=4800:break
        s.frames(1)
    else:raise AssertionError('Exit clock did not advance')
    s.check(4800<=state(s)['quit_ms']<5000,'game remains active just before the five-second deadline')
    try:
        for _ in range(100):s.frames(1)
    except (EOFError,BrokenPipeError):
        s.check(s.d.t.p.wait(timeout=5)==0,'five-second hold calls the menu exit successfully')
    else:s.check(False,'five-second hold exits')
    return s.result()


if __name__=='__main__':raise SystemExit(main())

