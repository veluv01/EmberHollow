#include "Game.h"
#include "src/assets/Assets.h"
#include <string.h>

namespace eh {

const Point Home={68,316};
const Point Throne={436,60};
const Point Shrines[Game::ShrineCount]={{100,276},{196,300},{100,164},{260,188},{364,276},{356,140}};
const Point Candy[8]={{76,284},{116,212},{180,276},{244,204},{308,180},{380,252},{380,124},{436,84}};
static int absolute(int n) { return n<0?-n:n; }
static int sign(int n) { return (n>0)-(n<0); }
static int distance(int x,int y,int a,int b) { return absolute(x-a)+absolute(y-b); }

Tile Game::tile(int tx,int ty) {
    if(tx<0||ty<0||tx>=Width||ty>=Height) return Wall;
    return static_cast<Tile>(assets::World[ty*Width+tx]);
}

uint8_t Game::random8() {
    randomState=uint16_t(randomState*25173u+13849u);
    return uint8_t(randomState>>8);
}

void Game::init() {
    memset(this,0,sizeof(*this));
    mode=Title; newChoice=true; saveOK=true; hp=10;
    progress.hp=10; progress.x=Home.x; progress.y=Home.y;
    x=Home.x; y=Home.y; facing=South; randomState=0xE117;
    for(uint8_t i=0;i<ShrineCount;++i) shrineHP[i]=6;
    boss.x=Throne.x; boss.y=Throne.y; boss.hp=24;
}

bool Game::load(const Progress &saved) {
    if(saved.active>1||saved.won>1||saved.cleared>AllShrines||saved.hp<1||saved.hp>10 ||
       saved.x<5||saved.y<5||saved.x>=Width*8-5||saved.y>=Height*8-5 ||
       (saved.won && saved.cleared!=AllShrines)) return false;
    progress=saved;
    if(!passable(saved.x,saved.y)) {
        progress.x=Home.x;progress.y=Home.y;
    }
    newChoice=!progress.active;
    return true;
}

void Game::start(bool fresh) {
    if(fresh) {
        const uint32_t best=progress.bestTicks;
        memset(&progress,0,sizeof(progress));
        progress.bestTicks=best; progress.hp=10;
        progress.x=Home.x; progress.y=Home.y; progress.active=1;
    }
    x=progress.x; y=progress.y; hp=progress.hp;
    mode=Play; guide=false; facing=South;endingTicks=0;newBest=false;
    swing=cooldown=riposte=guardAge=0;invulnerable=30;guarding=false;
    candies=0;randomState=0xE117;
    memset(enemies,0,sizeof(enemies));memset(particles,0,sizeof(particles));
    memset(&boss,0,sizeof(boss));boss.x=Throne.x;boss.y=Throne.y;boss.hp=progress.won?0:24;
    for(uint8_t i=0;i<ShrineCount;++i) shrineHP[i]=(progress.cleared&(1u<<i))?0:6;
    cameraX=x-64;cameraY=y-62;
    if(cameraX<0) cameraX=0;
    if(cameraY<0) cameraY=0;
    if(cameraX>Width*8-128) cameraX=Width*8-128;
    if(cameraY>Height*8-112) cameraY=Height*8-112;
    notice=90;visit();checkpoint();
}

bool Game::passable(int px,int py,bool flying) const {
    for(int dy=-3;dy<=3;dy+=6) for(int dx=-3;dx<=3;dx+=6) {
        const Tile t=tile((px+dx)>>3,(py+dy)>>3);
        if(t==Wall||(t==Gate&&progress.cleared!=AllShrines)||(!flying&&t==Lava)) return false;
    }
    return true;
}

void Game::effects(int px,int py,uint8_t colour,uint8_t count) {
    for(uint8_t i=0;i<ParticleCount&&count;++i) if(!particles[i].life) {
        Particle &p=particles[i];p.x=px;p.y=py;
        p.dx=int8_t(random8()%5)-2;p.dy=-int8_t(random8()%3+1);
        p.life=uint8_t(12+random8()%12);p.colour=colour;--count;
    }
}

bool Game::front(int px,int py,int reach) const {
    const int dx=px-x,dy=py-y;
    if(dx*dx+dy*dy>reach*reach) return false;
    switch(facing) {
        case South:return dy>=-3;
        case North:return dy<=3;
        case East:return dx>=-3;
        default:return dx<=3;
    }
}

void Game::hit(uint8_t damage,int ax,int ay,bool ground,DefeatCause cause) {
    if(invulnerable||mode!=Play) return;
    if(!ground&&guarding&&front(ax,ay,64)) {
        effects(x,y,guardAge<6?10:12,4);
        if(guardAge<6) {
            riposte=45;
            for(uint8_t i=0;i<EnemyCount;++i) if(enemies[i].hp&&distance(enemies[i].x,enemies[i].y,ax,ay)<8)
                enemies[i].stun=30;
        }
        return;
    }
    hp=hp>damage?hp-damage:0;invulnerable=36;effects(x,y,15,5);
    if(!hp) {
        mode=Fallen;endingTicks=0;defeatCause=cause;guarding=false;
        progress.hp=10;progress.x=Home.x;progress.y=Home.y;
        dirty=true;
    }
}

void Game::move(int dx,int dy) {
    const int nx=x+dx,ny=y+dy;
    if(passable(nx,ny)) { x=nx;y=ny;return; }
    // Rocks and the sealed gate block. Lava burns, without stranding the player.
    if(passable(nx,ny,true)) hit(2,nx,ny,true,MoltenGround);
}

void Game::attack() {
    const uint8_t power=riposte?2:1;riposte=0;
    for(uint8_t i=0;i<ShrineCount;++i) if(shrineHP[i]&&front(Shrines[i].x,Shrines[i].y,25)) {
        shrineHP[i]=shrineHP[i]>power?shrineHP[i]-power:0;
        effects(Shrines[i].x,Shrines[i].y,9,5);
        if(!shrineHP[i]) {
            progress.cleared|=uint8_t(1u<<i);hp=hp<9?hp+2:10;notice=90;
            checkpoint();effects(Shrines[i].x,Shrines[i].y,13,8);
        }
    }
    for(uint8_t i=0;i<EnemyCount;++i) {
        Enemy &e=enemies[i];if(!e.hp||!front(e.x,e.y,24)) continue;
        e.hp=e.hp>power?e.hp-power:0;e.flash=6;e.stun=14;
        effects(e.x,e.y,e.type==0?12:9,4);
    }
    if(boss.awake&&boss.hp&&front(boss.x,boss.y,32)&&boss.phase!=2) {
        boss.hp=boss.hp>power?boss.hp-power:0;boss.flash=6;effects(boss.x,boss.y-12,9,7);
        if(!boss.hp) {
            progress.won=1;mode=Victory;endingTicks=0;guarding=false;
            newBest=!progress.bestTicks||progress.ticks<progress.bestTicks;
            if(newBest) progress.bestTicks=progress.ticks;
            checkpoint();effects(boss.x,boss.y,10,12);
        }
    }
}

void Game::enemiesTick() {
    // Bounded pool: never allocate, and never leave enemies pursuing off-camera.
    if(frame%95==0) {
        for(uint8_t s=0;s<ShrineCount;++s) if(shrineHP[s]&&distance(x,y,Shrines[s].x,Shrines[s].y)<104) {
            for(uint8_t i=0;i<EnemyCount;++i) if(!enemies[i].hp) {
                const int ex=Shrines[s].x+((random8()&1)?20:-20),ey=Shrines[s].y+12;
                if(passable(ex,ey)) {
                    Enemy &e=enemies[i];memset(&e,0,sizeof(e));e.x=ex;e.y=ey;e.type=s%3;
                    e.hp=e.type==1?1:(e.type==2?3:2);e.timer=20;
                }
                break;
            }
        }
    }
    for(uint8_t i=0;i<EnemyCount;++i) {
        Enemy &e=enemies[i];if(!e.hp) continue;
        if(e.flash) --e.flash;
        if(distance(x,y,e.x,e.y)>160) { e.hp=0;continue; }
        if(e.stun) { --e.stun;continue; }
        if(e.timer) --e.timer;
        if(e.phase==1) {
            if(!e.timer) { if(distance(x,y,e.x,e.y)<18) hit(1,e.x,e.y);e.phase=2;e.timer=30; }
            continue;
        }
        if(e.phase==2) { if(!e.timer) e.phase=0;continue; }
        if(distance(x,y,e.x,e.y)<13) { e.phase=1;e.timer=e.type==1?10:18;continue; }
        const bool step=e.type==1||((frame+i)%2==0&&e.type==0)||(e.type==2&&(frame+i*3)%36<12);
        if(step) {
            const int dx=sign(x-e.x),dy=sign(y-e.y);
            if(passable(e.x+dx,e.y,e.type==1)) e.x+=dx;
            if(passable(e.x,e.y+dy,e.type==1)) e.y+=dy;
        }
    }
}

void Game::bossTick() {
    if(!boss.hp||progress.cleared!=AllShrines) return;
    if(!boss.awake) {
        if(y<96&&x>384) { boss.awake=true;boss.timer=40;notice=90; }
        else return;
    }
    // The Warden stays on its island. Retreating through the gate is safe.
    if(y>=96||x<384) return;
    if(boss.flash) --boss.flash;
    if(boss.timer) --boss.timer;
    if(boss.phase==0) {
        if(!boss.timer) {
            boss.targetX=x;boss.targetY=y;boss.phase=1;boss.timer=boss.hp<=12?22:32;
        }
    } else if(boss.phase==1) {
        if(!boss.timer) {
            boss.phase=2;boss.timer=12;
            if(passable(boss.targetX,boss.targetY)) { boss.x=boss.targetX;boss.y=boss.targetY; }
            const int dx=x-boss.targetX,dy=y-boss.targetY;
            if(dx*dx+dy*dy<=18*18) hit(2,boss.targetX,boss.targetY,true,Warden);
            effects(boss.targetX,boss.targetY,9,10);
        }
    } else if(!boss.timer) { boss.phase=0;boss.timer=boss.hp<=12?28:45; }
    if(boss.phase==0&&distance(x,y,boss.x,boss.y)<12) hit(1,boss.x,boss.y,false,Warden);
}

void Game::checkpoint() {
    progress.x=uint16_t(x);progress.y=uint16_t(y);progress.hp=hp?hp:10;
    progress.active=1;dirty=true;
}

void Game::visit() {
    const int cx=x/32,cy=y/32;
    for(int dy=-1;dy<=1;++dy) for(int dx=-1;dx<=1;++dx) {
        const int vx=cx+dx,vy=cy+dy;
        if(vx<0||vx>=16||vy<0||vy>=12) continue;
        const int index=vy*16+vx;progress.visited[index>>3]|=uint8_t(1u<<(index&7));
    }
}

bool Game::visited(int tx,int ty) const {
    if(tx<0||tx>=Width||ty<0||ty>=Height) return false;
    const int index=(ty/4)*16+tx/4;
    return (progress.visited[index>>3]&(1u<<(index&7)))!=0;
}

uint8_t Game::clearedCount() const {
    uint8_t n=0;for(uint8_t i=0;i<ShrineCount;++i) if(progress.cleared&(1u<<i)) ++n;return n;
}

int8_t Game::objective() const {
    int closest=32767;int8_t result=-1;
    for(uint8_t i=0;i<ShrineCount;++i) if(shrineHP[i]) {
        const int d=distance(x,y,Shrines[i].x,Shrines[i].y);
        if(d<closest) { closest=d;result=i; }
    }
    return result;
}

void Game::update(Input input) {
    ++frame;
    for(uint8_t i=0;i<ParticleCount;++i) if(particles[i].life) {
        Particle &p=particles[i];--p.life;p.x+=p.dx;p.y+=p.dy;if((p.life&3)==0) ++p.dy;
    }
    if(mode==Title) {
        if(input.pressed&(Left|Right|Up|Down)) newChoice=!newChoice;
        if(input.pressed&(B|Select)) guide=!guide;
        if(input.pressed&A) {
            if(guide) guide=false;
            else if(newChoice||!progress.active) { mode=Intro;storyPage=0; }
            else start(false);
        }
        return;
    }
    if(mode==Intro) {
        // Do not replace an existing checkpoint until the story is finished.
        if(input.pressed&B) start(true);
        else if(input.pressed&A) { if(++storyPage>=3) start(true); }
        return;
    }
    if(mode==Pause) {
        if(input.pressed&Select) guide=!guide;
        if(input.pressed&(Start|A|B)) { mode=Play;guide=false; }
        return;
    }
    if(mode==Fallen) {
        if(endingTicks<60000) ++endingTicks;
        if(endingTicks>=30) {
            if(input.pressed&A) start(false);
            else if(input.pressed&B) { mode=Title;newChoice=false;guide=false; }
        }
        return;
    }
    if(mode==Victory) {
        if(endingTicks<60000) ++endingTicks;
        if(frame%12==0) effects(x+(random8()%80)-40,y-30,9+(random8()%4),3);
        if(endingTicks>=45) {
            if(input.pressed&A) { mode=Title;newChoice=false;guide=false; }
            else if(input.pressed&B) { mode=Play;hp=10;notice=90;checkpoint(); }
        }
        return;
    }
    if(input.pressed&(Start|Select)) { checkpoint();mode=Pause;guide=(input.pressed&Select)!=0;guarding=false;return; }
    if(!progress.won) ++progress.ticks;
    if(notice) --notice;
    if(invulnerable) --invulnerable;
    if(cooldown) --cooldown;
    if(riposte) --riposte;
    guarding=(input.held&B)&&!swing;
    if(guarding) { if(guardAge<250) ++guardAge; } else guardAge=0;
    int dx=((input.held&Right)?1:0)-((input.held&Left)?1:0);
    int dy=((input.held&Down)?1:0)-((input.held&Up)?1:0);
    if(dx) facing=dx>0?East:West;else if(dy) facing=dy>0?South:North;
    const int speed=(guarding||(dx&&dy))?1:2;
    if(dx) move(dx*speed,0);
    if(dy&&mode==Play) move(0,dy*speed);
    if(mode!=Play) return;
    if((input.pressed&A)&&!cooldown&&!guarding) { swing=10;cooldown=14; }
    if(swing) { --swing;if(swing==7) attack(); }
    if(mode!=Play) { visit();return; }
    enemiesTick();
    if(mode!=Play) return;
    bossTick();
    if(mode!=Play) return;
    for(uint8_t i=0;i<8;++i) if(!(candies&(1u<<i))&&distance(x,y,Candy[i].x,Candy[i].y)<9&&hp<10) {
        candies|=uint16_t(1u<<i);hp=hp<9?hp+2:10;effects(x,y,13,5);
    }
    visit();
    cameraX=x-64;cameraY=y-62;
    if(cameraX<0) cameraX=0;
    if(cameraY<0) cameraY=0;
    if(cameraX>Width*8-128) cameraX=Width*8-128;
    if(cameraY>Height*8-112) cameraY=Height*8-112;
}

} // namespace eh

