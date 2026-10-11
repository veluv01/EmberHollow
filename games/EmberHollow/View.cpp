#include <CHGame.h>
#include "View.h"
#include "src/assets/Assets.h"

namespace eh {

static int absInt(int n) { return n<0?-n:n; }
static void centred(int y,const char *text,uint8_t colour=12) {
    text35((128-text35Width(text))/2,y,text,colour);
}
static void sprite(assets::SpriteId id,int x,int y) {
    const assets::Sprite &s=assets::Sprites[id];
    gfx_blit(s.pixels,x-s.width/2,y-s.height+3,s.width,s.height,0);
}
static void timerText(char *out,uint32_t ticks) {
    const uint32_t seconds=ticks/EH_FRAME_RATE;
    const uint32_t minutes=seconds/60>999?999:seconds/60;
    fmtInt(out,minutes);
    char *p=out;while(*p) ++p;*p++=':';*p++=char('0'+(seconds%60)/10);*p++=char('0'+seconds%10);*p=0;
}
static void heart(int x,int y,bool left,bool right) {
    gfx_line(x+1,y,x+2,y,left?15:3);gfx_line(x+4,y,x+5,y,right?15:3);
    gfx_fillRect(x,y+1,3,2,left?15:3);gfx_fillRect(x+3,y+1,3,2,right?15:3);
    gfx_line(x+1,y+3,x+4,y+3,right?15:3);gfx_line(x+2,y+4,x+3,y+4,left?15:3);
}
static void arrow(int x,int y,int dx,int dy,uint8_t colour) {
    if(absInt(dx)>absInt(dy)) {
        const int sign=dx>0?1:-1;
        gfx_line(x-sign*3,y,x+sign*3,y,colour);
        gfx_line(x+sign*3,y,x,y-3,colour);gfx_line(x+sign*3,y,x,y+3,colour);
    } else {
        const int sign=dy>0?1:-1;
        gfx_line(x,y-sign*3,x,y+sign*3,colour);
        gfx_line(x,y+sign*3,x-3,y,colour);gfx_line(x,y+sign*3,x+3,y,colour);
    }
}

void beginGraphics() {
    gfx_begin(GFX_DIV4,GFX_12BPP); // 12 MHz shared SPI: comfortable on breadboards.
    gfx_setPalette(assets::Palette,16);
}

static void help(bool paused) {
    panel(5,29,118,95,3,0,4);
    centred(36,"HOW TO PLAY",10);
    text35(13,48,"D-PAD   WALK",12);
    text35(13,58,"A       SWORD",12);
    text35(13,68,"B HOLD  GUARD",12);
    text35(13,78,"B TAP   PARRY",12);
    text35(13,88,"START   MAP",12);
    centred(100,"HOLD START 5S TO QUIT",9);
    centred(114,paused?"A RESUME  SELECT MAP":"A BACK",13);
}

static void embers(const Game &g,bool peaceful) {
    gfx_clear(0);
    for(uint8_t i=0;i<20;++i) {
        const int x=(i*37+11)%128;
        const int y=(i*19+120-(g.frame/(peaceful?5:2))%120)%120;
        gfx_pixel(x,y,peaceful?13:7);
        if(i%4==0) gfx_pixel(x,y-1,peaceful?10:9);
    }
    gfx_line(5,54,122,54,3);
}

static void story(const Game &g) {
    embers(g,false);
    const char *heading[]={"THE LAST LANTERNS","YOU ARE WICK","BEFORE DAWN"};
    static const char *const lines[3][5]={
        {"Each Halloween, six lanterns","kept Ember Hollow safe.","The Ash Warden cursed them,","raising monsters and tearing","the earth open with lava."},
        {"You are Wick, a pumpkin","guardian with one last spark.","Take up your sword and shield.","Cross the molten rivers and","bring the lanterns back."},
        {"Break all six cursed shrines","to open the northern gate.","Face the Ash Warden there.","Dodge his fire. End the curse.","Let the Hollow shine again."}
    };
    centred(7,heading[g.storyPage],10);
    if(g.storyPage==0) {
        sprite(assets::ShrineLive,24,49);sprite(assets::Boss0,64,49);sprite(assets::ShrineLive,104,49);
    } else if(g.storyPage==1) {
        sprite(assets::HomeSprite,41,49);sprite(assets::HeroDown0,79,49);
        gfx_line(91,47,95,31,12);gfx_line(88,43,95,45,9);
    } else {
        for(uint8_t i=0;i<6;++i) sprite(assets::ShrineClear,14+i*20,48);
    }
    for(uint8_t i=0;i<5;++i) centred(63+i*9,lines[g.storyPage][i],i==4?11:12);
    for(uint8_t i=0;i<3;++i) gfx_fillRect(54+i*8,112,4,2,i==g.storyPage?9:3);
    text35(5,122,g.storyPage==2?"A BEGIN":"A NEXT",10);
    text35(98,122,"B SKIP",11);
}

static void ending(const Game &g) {
    const bool won=g.mode==Victory;
    embers(g,won);
    centred(7,won?"THE HOLLOW IS SAVED":"YOUR SPARK FADES",won?10:15);
    if(won) {
        sprite(assets::ShrineClear,19,49);sprite(assets::HomeSprite,63,49);
        sprite(assets::HeroDown0,84,49);sprite(assets::ShrineClear,110,49);
        centred(61,"The lanterns glow again.",12);
        centred(71,"Wick brought the dawn home.",11);
    } else {
        sprite(assets::HeroDown0,64,49);
        gfx_fillEllipse(64,52,14,2,3);
        const int rise=(g.endingTicks/4)%18;
        gfx_fillRect(63,31-rise,2,3,9);gfx_pixel(63,30-rise,10);
        centred(61,"One ember still survives.",12);
        centred(71,"Your cleared shrines remain.",11);
    }
    char buf[12];timerText(buf,g.progress.ticks);
    text35(9,84,"TIME",4);text35(31,84,buf,12);
    if(won) { text35(71,84,"BEST",4);timerText(buf,g.progress.bestTicks);text35(92,84,buf,12); }
    else { text35(73,84,"SHRINES",4);fmtInt(buf,g.clearedCount());text35(105,84,buf,13);text35(110,84,"/6",4); }
    if(won) {
        centred(97,g.newBest?"NEW BEST TIME!":"ALL SIX LANTERNS RESTORED",10);
        if(g.endingTicks>=45) { centred(112,"A TITLE   B EXPLORE",12);centred(122,"HOLD START 5S FOR MENU",4); }
    } else {
        const char *tip=g.defeatCause==MoltenGround?"TIP: CROSS LAVA ON BRIDGES":
                        (g.defeatCause==Warden?"TIP: STEP OUTSIDE THE CIRCLE":"TIP: FACE ATTACKS AND TAP B");
        centred(97,tip,9);
        if(g.endingTicks>=30) { centred(112,"A RETRY   B TITLE",12);centred(122,"RETRY RETURNS TO THE HUT",4); }
    }
}

static void title(const Game &g) {
    gfx_blit(assets::TitleScene,0,0,128,128,-1);
    if(g.guide) { help(false);return; }
    if(g.progress.active) {
        text35(19,111,"CONTINUE",g.newChoice?4:10);
        text35(80,111,"NEW",g.newChoice?10:4);
        gfx_line(g.newChoice?78:17,119,g.newChoice?98:51,119,9);
        centred(122,"A START   B HELP",11);
    } else {
        centred(111,"PRESS A TO START",10);
        centred(121,"B HOW TO PLAY",11);
    }
}

static void map(const Game &g) {
    gfx_clear(0);
    centred(4,"THE HOLLOW",10);
    for(int ty=0;ty<Game::Height;++ty) for(int tx=0;tx<Game::Width;++tx) {
        if(!g.visited(tx,ty)) continue;
        const Tile t=Game::tile(tx,ty);
        const uint8_t c=t==Wall?4:(t==Lava?7:(t==Bridge?11:(t==Gate?(g.progress.cleared==Game::AllShrines?11:15):2)));
        gfx_fillRect(tx*2,16+ty*2,2,2,c);
    }
    for(uint8_t i=0;i<Game::ShrineCount;++i) if(g.visited(Shrines[i].x/8,Shrines[i].y/8)) {
        const int sx=Shrines[i].x/4,sy=16+Shrines[i].y/4;
        gfx_fillRect(sx-2,sy-2,5,5,g.shrineHP[i]?15:13);gfx_pixel(sx,sy,0);
    }
    if(g.visited(Throne.x/8,Throne.y/8)) gfx_rect(Throne.x/4-2,Throne.y/4+14,5,5,9);
    if((g.frame/8)&1) gfx_fillRect(g.x/4-1,16+g.y/4-1,3,3,12);
    gfx_fillRect(0,113,128,15,0);
    centred(116,"A RESUME  SELECT HELP",12);
    if(!g.saveOK) text35(2,123,"SAVE UNAVAILABLE",15);
    else text35(2,123,"CHECKPOINT SAVED",13);
    if(g.guide) help(true);
}

static void world(const Game &g) {
    const int camX=g.cameraX,camY=g.cameraY;
    gfx_setClip(0,16,128,112);
    const int tx0=camX/8,ty0=camY/8;
    for(int ty=ty0;ty<=ty0+14&&ty<Game::Height;++ty) for(int tx=tx0;tx<=tx0+16&&tx<Game::Width;++tx) {
        const Tile t=Game::tile(tx,ty);uint8_t art=t;
        if(t==Floor) { const int pattern=(tx*17+ty*13)%11;art=pattern<2?10+pattern:0; }
        if(t==Lava) { const uint8_t phase=((g.frame/8)+tx/3+ty/2)%3;art=phase==0?2:7+phase; }
        if(t==Gate&&g.progress.cleared==Game::AllShrines) art=3;
        const int sx=tx*8-camX,sy=ty*8-camY+16;
        gfx_blit(assets::Tiles[art],sx,sy,8,8,-1);
        // Warm bank edges give the molten channels a clean, readable boundary.
        if(t==Lava) {
            if(Game::tile(tx,ty-1)!=Lava) gfx_line(sx,sy,sx+7,sy,9);
            if(Game::tile(tx-1,ty)!=Lava) gfx_line(sx,sy,sx,sy+7,8);
        }
    }
    sprite(assets::HomeSprite,Home.x-camX,Home.y-camY+16);
    for(uint8_t i=0;i<Game::ShrineCount;++i) {
        const int sx=Shrines[i].x-camX,sy=Shrines[i].y-camY+16;
        sprite(g.shrineHP[i]?assets::ShrineLive:assets::ShrineClear,sx,sy);
        if(g.shrineHP[i]&&absInt(g.x-Shrines[i].x)+absInt(g.y-Shrines[i].y)<44) {
            for(uint8_t n=0;n<6;++n) gfx_fillRect(sx-9+n*3,sy-25,2,2,n<g.shrineHP[i]?9:3);
        }
    }
    for(uint8_t i=0;i<8;++i) if(!(g.candies&(1u<<i)))
        sprite(assets::CandySprite,Candy[i].x-camX,Candy[i].y-camY+16-((g.frame/12)&1));
    // Draw entities in foot order so passing behind a creature reads correctly.
    uint8_t order[Game::EnemyCount+2];uint8_t count=0;
    for(uint8_t i=0;i<Game::EnemyCount;++i) if(g.enemies[i].hp) order[count++]=i;
    order[count++]=Game::EnemyCount;
    if(g.boss.hp) order[count++]=Game::EnemyCount+1;
    for(uint8_t i=1;i<count;++i) {
        const uint8_t id=order[i];
        const int foot=id==Game::EnemyCount?g.y:(id==Game::EnemyCount+1?g.boss.y:g.enemies[id].y);
        uint8_t j=i;
        while(j) {
            const uint8_t prior=order[j-1];
            const int before=prior==Game::EnemyCount?g.y:(prior==Game::EnemyCount+1?g.boss.y:g.enemies[prior].y);
            if(before<=foot) break;
            order[j]=prior;--j;
        }
        order[j]=id;
    }
    if(g.boss.awake&&g.boss.phase) {
        const int sx=g.boss.targetX-camX,sy=g.boss.targetY-camY+16;
        gfx_circle(sx,sy,18,g.boss.phase==2?9:15);
        gfx_circle(sx,sy,14,g.boss.phase==2?8:6);
        gfx_line(sx-5,sy,sx+5,sy,10);gfx_line(sx,sy-5,sx,sy+5,10);
    }
    for(uint8_t n=0;n<count;++n) {
        const uint8_t id=order[n];
        if(id==Game::EnemyCount) {
            const int sx=g.x-camX,sy=g.y-camY+16;
            gfx_fillEllipse(sx,sy+2,6,2,0);
            if(!g.invulnerable||(g.frame&2)) {
                const uint8_t anim=uint8_t((g.frame/6)&1);
                const uint8_t base=g.facing==South?0:(g.facing==North?2:(g.facing==East?4:6));
                sprite(static_cast<assets::SpriteId>(base+anim),sx,sy);
                if(g.guarding) {
                    const int dx=g.facing==East?7:(g.facing==West?-7:0);
                    const int dy=g.facing==South?3:(g.facing==North?-12:-4);
                    gfx_fillRect(sx+dx-2,sy+dy-2,5,6,g.guardAge<6?10:11);gfx_rect(sx+dx-2,sy+dy-2,5,6,4);
                }
                if(g.swing) {
                    int dx=g.facing==East?1:(g.facing==West?-1:0);
                    int dy=g.facing==South?1:(g.facing==North?-1:0);
                    const int side=int(g.swing)-5;
                    const int tipX=sx+dx*19-dy*side,tipY=sy-5+dy*19+dx*side;
                    gfx_line(sx+dx*7,sy-5+dy*7,tipX,tipY,12);
                    gfx_line(tipX+dy*2,tipY-dx*2,tipX-dy*4,tipY+dx*4,10);
                }
            }
        } else if(id==Game::EnemyCount+1) {
            const int sx=g.boss.x-camX,sy=g.boss.y-camY+16;
            gfx_fillEllipse(sx,sy+2,16,3,0);
            if(!g.boss.flash||(g.frame&1)) sprite((g.frame/10)&1?assets::Boss1:assets::Boss0,sx,sy);
        } else {
            const Enemy &e=g.enemies[id];const int sx=e.x-camX,sy=e.y-camY+16;
            gfx_fillEllipse(sx,sy+2,5,2,0);
            if(!e.flash||(g.frame&1)) sprite(static_cast<assets::SpriteId>(8+e.type*2+((g.frame/8)&1)),sx,sy-(e.type==1?4:0));
            if(e.phase==1) { text35(sx-1,sy-24,"!",15);gfx_line(sx-5,sy+3,sx+5,sy+3,15); }
            if(e.stun&&((g.frame/4)&1)) gfx_pixel(sx,sy-21,10);
        }
    }
    for(uint8_t i=0;i<Game::ParticleCount;++i) if(g.particles[i].life) {
        const Particle &p=g.particles[i];gfx_fillRect(p.x-camX,p.y-camY+16,2,2,p.colour);
    }
    gfx_resetClip();
}

static void hud(const Game &g) {
    gfx_fillRect(0,0,128,16,0);gfx_line(0,15,127,15,3);
    for(uint8_t i=0;i<5;++i) heart(3+i*9,5,g.hp>i*2,g.hp>i*2+1);
    char buf[12];fmtInt(buf,g.clearedCount());text35(52,5,buf,13);text35(57,5,"/6",4);
    timerText(buf,g.progress.ticks);text35(77,5,buf,11);
    const int8_t goal=g.objective();const Point target=goal<0?Throne:Shrines[goal];
    if(!g.progress.won) arrow(120,7,target.x-g.x,target.y-g.y,goal<0?15:9);
    if(g.riposte&&g.mode==Play) { gfx_fillRect(42,18,44,8,0);centred(20,"PARRY!",10); }
    if(g.boss.awake&&g.boss.hp&&g.y<96&&g.x>384) {
        gfx_fillRect(0,110,128,18,0);gfx_line(0,110,127,110,3);
        text35(4,113,"ASH WARDEN",g.boss.hp<=12?15:9);
        text35(51,113,g.boss.phase==1?"DODGE":(g.boss.phase==2?"FIRE":"STRIKE"),12);
        fmtInt(buf,g.boss.hp);text35(96,113,buf,12);text35(105,113,"/24",4);
        gfx_rect(4,121,120,5,4);gfx_fillRect(5,122,(g.boss.hp*118+23)/24,3,g.boss.hp<=12?15:8);
    } else if(g.notice&&g.mode==Play) {
        gfx_fillRect(4,117,120,10,0);
        centred(120,g.progress.won?"THE HOLLOW IS SAFE":(g.progress.cleared==Game::AllShrines?"THE NORTH GATE IS OPEN":"BREAK SIX CURSED SHRINES"),10);
    }
}

static void scene(const Game &g) {
    if(g.mode==Title) { title(g);return; }
    if(g.mode==Intro) { story(g);return; }
    if(g.mode==Pause) { map(g);return; }
    if(g.mode==Fallen||g.mode==Victory) { ending(g);return; }
    world(g);hud(g);
}

void draw(const Game &g,uint16_t quitMilliseconds) {
    scene(g);
    if(quitMilliseconds<500) return;
    panel(7,39,114,53,3,0,9);
    centred(46,"RETURN TO MENU",10);
    char countdown[]="HOLD START: 5";
    countdown[12]=char('0'+(5000-quitMilliseconds+999)/1000);
    centred(58,countdown,12);
    gfx_rect(16,69,96,6,4);gfx_fillRect(17,70,94ul*quitMilliseconds/5000,4,9);
    centred(81,"RELEASE TO CANCEL",11);
}

} // namespace eh

