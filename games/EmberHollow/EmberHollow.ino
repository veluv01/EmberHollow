#include <CHGame.h>
#include "Game.h"
#include "View.h"
#include "QuitHold.h"

static eh::Game game;
static eh::QuitHold quitHold;
static const uint32_t SAVE_MAGIC=save::magic("EHLO");

#if CHGAME_DEBUG
// Repeatable simulator fixtures, absent from the release image.
static void number(uint32_t n) { char b[12];fmtInt(b,n);dbg::print(b); }
static bool debugCommand(char command,const char *args) {
    if(command=='Z') {
        dbg::print("STATE mode=");number(game.mode);dbg::print(" x=");number(game.x);
        dbg::print(" y=");number(game.y);dbg::print(" hp=");number(game.hp);
        dbg::print(" cleared=");number(game.progress.cleared);dbg::print(" boss=");number(game.boss.hp);
        dbg::print(" ticks=");number(game.progress.ticks);dbg::print(" phase=");number(game.boss.phase);
        dbg::print(" story=");number(game.storyPage);dbg::print(" quit_ms=");number(quitHold.elapsed);
        dbg::print("\n");return true;
    }
    if(command=='W') {
        const int x=dbg::parseNum(args,10),y=dbg::parseNum(args,10);
        const int face=dbg::parseNum(args,10);
        if(!game.passable(x,y)||face>3) return false;
        game.x=x;game.y=y;game.facing=static_cast<eh::Direction>(face);return true;
    }
    if(command=='C') {
        const unsigned mask=dbg::parseNum(args,10);if(mask>63) return false;
        game.progress.cleared=mask;
        for(uint8_t i=0;i<eh::Game::ShrineCount;++i) game.shrineHP[i]=(mask&(1u<<i))?0:6;
        return true;
    }
    if(command=='H') {
        const unsigned hp=dbg::parseNum(args,10);if(hp<1||hp>10) return false;
        game.hp=hp;game.invulnerable=30;return true;
    }
    if(command=='V') {
        // Restart application state, retaining the simulator's flash pages.
        game.init();quitHold=eh::QuitHold{};eh::Progress saved={};
        if(save::load(SAVE_MAGIC,EH_SAVE_VERSION,saved)) game.load(saved);
        game.saveOK=save::available();return true;
    }
    if(command=='J') {
        const unsigned hp=dbg::parseNum(args,10);if(hp<1||hp>24) return false;
        game.boss.hp=hp;game.boss.phase=0;game.boss.timer=90;game.boss.awake=true;
        game.boss.x=eh::Throne.x;game.boss.y=eh::Throne.y;return true;
    }
    if(command=='E') {
        eh::Enemy e={};e.x=game.x+10;e.y=game.y;e.hp=2;e.phase=1;e.timer=3;
        game.enemies[0]=e;game.invulnerable=0;game.facing=eh::East;return true;
    }
    return false;
}
#endif

void setup() {
    chgame.boot();
    chgame.startExits=false; // This game uses a five-second hold below.
    dbg::begin("EHLO " EH_VERSION);
    game.init();
    eh::beginGraphics();
    eh::Progress saved={};
    if(save::load(SAVE_MAGIC,EH_SAVE_VERSION,saved)) game.load(saved);
    game.saveOK=save::available();
    chgame.setFrameRate(EH_FRAME_RATE);
#if CHGAME_DEBUG
    dbg::hook=debugCommand;
#endif
}

void loop() {
    dbg::poll();
    if(!chgame.nextFrame()) return;
    dbg::markUpdateStart();
    chgame.pollButtons();
    eh::Input input={0,0};
    const uint8_t buttons[]={A_BUTTON,B_BUTTON,UP_BUTTON,DOWN_BUTTON,LEFT_BUTTON,RIGHT_BUTTON,START_BUTTON,SELECT_BUTTON};
    for(uint8_t i=0;i<8;++i) {
        if(chgame.pressed(buttons[i])) input.held|=uint8_t(1u<<i);
        if(chgame.justPressed(buttons[i])) input.pressed|=uint8_t(1u<<i);
    }
    const bool quit=quitHold.update(millis(),(input.held&eh::Start)!=0);
    game.update(input);
    // Both saving and all framebuffer writes happen after the previous DMA.
    gfx_wait();
    if(quit&&(game.mode==eh::Play||game.mode==eh::Pause)) game.checkpoint();
    if(game.dirty) {
        game.saveOK=save::store(SAVE_MAGIC,EH_SAVE_VERSION,game.progress);
        game.dirty=false; // Never hammer a failing save page every frame.
    }
    dbg::markRenderStart();
    if(quit) chgame.exitToMenu();
    eh::draw(game,quitHold.elapsed);
    dbg::markRenderEnd();
    gfx_flushAsync();
}

