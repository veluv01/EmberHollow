#include "../../Game.h"
#include "../../QuitHold.h"
#include "../../src/assets/Assets.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <queue>
#include <vector>

using namespace eh;
static unsigned checks;
#define CHECK(x) do { ++checks;assert(x); } while(0)
static void tick(Game &g,unsigned n=1,uint8_t held=0) {
    while(n--) g.update({held,0});
}
static void tap(Game &g,uint8_t button) { g.update({button,button});g.update({0,0}); }
static Game fresh() { Game g;g.init();g.start(true);return g; }

static void titleAndPause() {
    Game g;g.init();CHECK(g.mode==Title);CHECK(!g.progress.active);
    tap(g,B);CHECK(g.guide);tap(g,A);CHECK(!g.guide&&g.mode==Title);
    tap(g,A);CHECK(g.mode==Intro);CHECK(g.storyPage==0);
    tick(g,2000,Up|A);CHECK(!g.progress.ticks&&!g.progress.active&&!g.dirty);
    tap(g,A);CHECK(g.storyPage==1);tap(g,A);CHECK(g.storyPage==2);
    tap(g,A);CHECK(g.mode==Play&&!g.swing);CHECK(g.hp==10);CHECK(g.x==Home.x);
    CHECK(g.cameraY>0);CHECK(g.dirty);CHECK(g.visited(Home.x/8,Home.y/8));
    tick(g,30);const uint32_t now=g.progress.ticks;
    tap(g,Start);CHECK(g.mode==Pause);const uint32_t paused=g.progress.ticks;
    tick(g,90);CHECK(g.progress.ticks==paused);CHECK(paused==now);
    tap(g,Select);CHECK(g.guide);tap(g,A);CHECK(g.mode==Play&&!g.guide);
}

static void terrain() {
    Game g=fresh();
    g.x=19*8-4;g.y=31*8+4;g.invulnerable=0;
    const int before=g.x;g.update({Right,Right});CHECK(g.x==before);CHECK(g.hp==8);
    tick(g,12,Right);CHECK(g.hp==8);CHECK(g.x==before);
    g.x=19*8-4;g.y=37*8+4;tick(g,18,Right);CHECK(g.x>21*8);
    g.x=16;g.y=16;tick(g,30,Left);CHECK(g.x>=11);
    CHECK(!g.passable(424,100));g.progress.cleared=63;CHECK(g.passable(424,100));
    // Every shrine, candy and the gate approach is reachable from home.
    for(unsigned open=0;open<2;++open) {
        g.progress.cleared=open?63:0;
        const int w=Game::Width,h=Game::Height;
        std::vector<bool> seen(w*h,false);std::queue<int> queue;
        const int start=(Home.y/8)*w+Home.x/8;seen[start]=true;queue.push(start);
        while(!queue.empty()) {
            const int cell=queue.front();queue.pop();const int x=cell%w,y=cell/w;
            const int dx[]={1,-1,0,0},dy[]={0,0,1,-1};
            for(unsigned i=0;i<4;++i) {
                const int nx=x+dx[i],ny=y+dy[i];
                if(nx<0||ny<0||nx>=w||ny>=h) continue;
                const int next=ny*w+nx;
                if(!seen[next]&&g.passable(nx*8+4,ny*8+4)) { seen[next]=true;queue.push(next); }
            }
        }
        for(const Point &p:Shrines) CHECK(seen[(p.y/8)*w+p.x/8]);
        for(unsigned i=0;i<7;++i) CHECK(seen[(Candy[i].y/8)*w+Candy[i].x/8]);
        CHECK(seen[(Throne.y/8)*w+Throne.x/8]==bool(open));
    }
}

static void introAndQuit() {
    Game g=fresh();g.progress.cleared=5;g.progress.bestTicks=600;g.checkpoint();
    const Progress saved=g.progress;g.init();CHECK(g.load(saved));
    tap(g,A);CHECK(g.mode==Play&&g.progress.cleared==5);
    g.mode=Title;g.newChoice=true;g.dirty=false;
    tap(g,A);CHECK(g.mode==Intro&&g.storyPage==0);
    CHECK(g.progress.cleared==5&&!g.dirty);
    tap(g,B);CHECK(g.mode==Play&&g.progress.cleared==0&&g.progress.bestTicks==600);
    CHECK(g.x==Home.x&&!g.swing&&!g.guarding);
    QuitHold q;
    CHECK(!q.update(100,true));CHECK(q.elapsed==0);
    CHECK(!q.update(3100,true));CHECK(!q.update(5099,true));
    CHECK(q.update(5100,true));CHECK(q.elapsed==5000);
    CHECK(!q.update(5101,false)&&q.elapsed==0);
    CHECK(!q.update(9000,true));CHECK(!q.update(12000,true));
    CHECK(!q.update(12001,false));CHECK(!q.update(15000,true));
    CHECK(!q.update(19999,true));CHECK(q.update(20000,true));
    q.update(0,false);
    CHECK(!q.update(0xfffffff0u,true));
    CHECK(!q.update(uint32_t(0xfffffff0u+4999u),true));
    CHECK(q.update(uint32_t(0xfffffff0u+5000u),true));
}

static void shrinesAndHealing() {
    Game g=fresh();g.hp=5;g.frame=1;
    for(unsigned shrine=0;shrine<6;++shrine) {
        g.x=Shrines[shrine].x;g.y=Shrines[shrine].y+16;g.facing=North;
        for(unsigned blow=0;blow<6;++blow) {
            memset(g.enemies,0,sizeof(g.enemies));g.invulnerable=40;
            tap(g,A);tick(g,14);
        }
        CHECK(g.shrineHP[shrine]==0);CHECK(g.progress.cleared&(1u<<shrine));
        CHECK(g.dirty);CHECK(g.progress.x==g.x);CHECK(g.progress.hp==g.hp);
    }
    CHECK(g.clearedCount()==6);CHECK(g.progress.cleared==63);CHECK(g.hp==10);CHECK(g.objective()==-1);
    g.hp=6;g.x=Candy[0].x;g.y=Candy[0].y;tick(g);CHECK(g.hp==8);CHECK(g.candies&1);
    tick(g);CHECK(g.hp==8);
}

static void attackAndGuard() {
    Game g=fresh();g.frame=1;g.x=120;g.y=312;g.facing=East;g.invulnerable=0;
    Enemy &e=g.enemies[0];e.x=g.x+10;e.y=g.y;e.hp=3;e.type=0;e.phase=1;e.timer=1;
    tap(g,B);CHECK(g.hp==10);CHECK(g.riposte>0);CHECK(e.stun>0);
    tap(g,A);tick(g,3);CHECK(e.hp==1);CHECK(!g.riposte);
    tick(g,18);e.hp=2;e.stun=0;e.x=g.x-10;e.y=g.y;e.phase=1;e.timer=1;
    g.invulnerable=0;tap(g,B);CHECK(g.hp==9); // Shield only protects the front.
    Game h=fresh();h.x=120;h.y=312;h.facing=East;h.invulnerable=0;
    tick(h,10,B);Enemy &a=h.enemies[0];a.x=h.x+10;a.y=h.y;a.hp=2;a.phase=1;a.timer=1;
    tick(h,1,B);CHECK(h.hp==10);CHECK(h.riposte==0); // Late guard blocks, no parry reward.
}

static void saveAndDeath() {
    Game g=fresh();g.progress.cleared=5;g.shrineHP[0]=g.shrineHP[2]=0;
    g.progress.bestTicks=600;g.progress.ticks=840;g.checkpoint();
    Progress record=g.progress;Game h;h.init();CHECK(h.load(record));h.start(false);
    CHECK(h.progress.cleared==5);CHECK(h.shrineHP[0]==0);CHECK(h.shrineHP[1]==6);
    CHECK(h.progress.ticks==840);CHECK(h.progress.bestTicks==600);
    record.cleared=64;CHECK(!h.load(record));record=g.progress;record.hp=0;CHECK(!h.load(record));
    record=g.progress;record.x=65535;CHECK(!h.load(record));
    g.x=19*8-4;g.y=31*8+4;g.hp=1;g.invulnerable=0;g.update({Right,Right});
    CHECK(g.mode==Fallen);CHECK(g.progress.x==Home.x);CHECK(g.progress.hp==10);
    CHECK(g.defeatCause==MoltenGround);tap(g,A);CHECK(g.mode==Fallen);
    const uint32_t time=g.progress.ticks;tick(g,32);CHECK(time==g.progress.ticks);
    tap(g,A);CHECK(g.mode==Play);CHECK(g.x==Home.x);CHECK(g.hp==10);
    CHECK(g.progress.cleared==5);CHECK(g.progress.bestTicks==600);
}

static void bossFight() {
    Game g=fresh();g.progress.cleared=63;memset(g.shrineHP,0,sizeof(g.shrineHP));
    g.x=436;g.y=84;g.invulnerable=0;g.candies=255;tick(g);CHECK(g.boss.awake);
    tick(g,40);CHECK(g.boss.phase==1);
    // An eruption hits at the advertised target, and bypasses a shield.
    const int tx=g.boss.targetX,ty=g.boss.targetY;
    g.x=tx;g.y=ty;g.hp=10;g.invulnerable=0;tick(g,32,B);CHECK(g.hp==8);
    // Walking outside the 18px circle escapes it.
    g.boss.phase=1;g.boss.timer=1;g.boss.targetX=436;g.boss.targetY=60;
    g.x=460;g.y=60;g.invulnerable=0;g.hp=10;tick(g);CHECK(g.hp==10);
    // A real final attack moves through the same combat and victory path.
    g.boss.phase=0;g.boss.timer=80;g.boss.hp=1;g.boss.x=436;g.boss.y=60;
    g.x=436;g.y=80;g.facing=North;g.cooldown=0;g.progress.ticks=900;g.progress.bestTicks=0;
    tap(g,A);tick(g,3);CHECK(g.mode==Victory);CHECK(g.progress.won);
    CHECK(!g.boss.hp);CHECK(g.progress.bestTicks==g.progress.ticks);CHECK(g.dirty);
    CHECK(g.newBest);const uint32_t best=g.progress.bestTicks;
    tap(g,A);CHECK(g.mode==Victory);tick(g,46);CHECK(g.progress.ticks==best);
    tap(g,B);CHECK(g.mode==Play&&g.hp==10&&g.progress.won&&!g.boss.hp);
    tick(g,90);CHECK(g.progress.ticks==best);
    g.mode=Victory;g.endingTicks=50;tap(g,A);CHECK(g.mode==Title);
    g.start(true);CHECK(!g.progress.won&&g.progress.cleared==0);CHECK(g.progress.bestTicks==best);
}

static void soakAndAssets() {
    for(unsigned i=0;i<64*48;++i) CHECK(assets::World[i]<=Gate);
    for(unsigned i=0;i<assets::SpriteCount;++i) CHECK(assets::Sprites[i].width>0&&assets::Sprites[i].height>0);
    Game g=fresh();unsigned r=0x10203040;
    for(unsigned i=0;i<100000;++i) {
        r=r*1664525u+1013904223u;
        const uint8_t held=uint8_t(r>>24);
        g.update({held,uint8_t(i%8==0?held:0)});
        CHECK(g.x>=0&&g.x<512&&g.y>=0&&g.y<384);CHECK(g.hp<=10);
        CHECK(g.progress.cleared<=63);CHECK(g.cameraX>=0&&g.cameraX<=384);
        CHECK(g.cameraY>=0&&g.cameraY<=272);
    }
}

int main() {
    titleAndPause();introAndQuit();terrain();shrinesAndHealing();attackAndGuard();saveAndDeath();bossFight();soakAndAssets();
    printf("Ember Hollow: %u checks passed (controls, paths, lava, shrines, combat, save, boss, soak).\n",checks);
}

