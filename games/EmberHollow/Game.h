#pragma once
#include <stdint.h>
#include "config.h"

namespace eh {

enum Button : uint8_t { A=1, B=2, Up=4, Down=8, Left=16, Right=32, Start=64, Select=128 };
enum Mode : uint8_t { Title, Play, Pause, Fallen, Victory, Intro };
enum DefeatCause : uint8_t { Creature, MoltenGround, Warden };
enum Tile : uint8_t { Floor, Wall, Lava, Bridge, Grave, Pumpkin, Bones, Gate };
enum Direction : uint8_t { South, West, North, East };
struct Point { int16_t x, y; };
struct Input { uint8_t held, pressed; };

// Fixed layout, no pointers: the save is versioned independently of the image.
struct Progress {
    uint32_t ticks, bestTicks;
    uint16_t x, y;
    uint8_t cleared, hp, active, won;
    uint8_t visited[24];
};
static_assert(sizeof(Progress) <= 244, "Progress must fit a CHGame save page");

struct Enemy {
    int16_t x, y;
    uint8_t type, hp, timer, phase, stun, flash;
};
struct Particle { int16_t x,y; int8_t dx,dy; uint8_t life, colour; };
struct Boss {
    int16_t x,y,targetX,targetY;
    uint8_t hp, phase, timer, flash;
    bool awake;
};

class Game {
public:
    static const int Width=64, Height=48, TileSize=8;
    static const uint8_t ShrineCount=6, EnemyCount=8, ParticleCount=16;
    static const uint8_t AllShrines=63;

    Progress progress;
    Enemy enemies[EnemyCount];
    Particle particles[ParticleCount];
    Boss boss;
    Mode mode;
    Direction facing;
    uint32_t frame;
    uint16_t candies;
    uint16_t endingTicks;
    int16_t x,y,cameraX,cameraY;
    uint8_t shrineHP[ShrineCount];
    uint8_t hp, swing, cooldown, invulnerable, guardAge, riposte, notice;
    uint8_t storyPage;
    DefeatCause defeatCause;
    bool guarding, dirty, saveOK, newChoice, guide;
    bool newBest;

    void init();
    bool load(const Progress &saved);
    void start(bool fresh);
    void update(Input input);
    void checkpoint();
    uint8_t clearedCount() const;
    int8_t objective() const;
    bool visited(int tx,int ty) const;
    static Tile tile(int tx,int ty);
    bool passable(int px,int py,bool flying=false) const;

private:
    uint16_t randomState;
    uint8_t random8();
    void move(int dx,int dy);
    void attack();
    void hit(uint8_t damage,int attackerX,int attackerY,bool ground=false,DefeatCause cause=Creature);
    void enemiesTick();
    void bossTick();
    void effects(int px,int py,uint8_t colour,uint8_t count);
    void visit();
    bool front(int px,int py,int reach) const;
};

extern const Point Shrines[Game::ShrineCount];
extern const Point Candy[8];
extern const Point Home;
extern const Point Throne;

} // namespace eh

