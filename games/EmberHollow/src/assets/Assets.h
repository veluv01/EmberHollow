// Generated asset storage is produced by tools/assets.py.
#pragma once
#include <stdint.h>
namespace eh { namespace assets {
struct Sprite { const uint8_t *pixels; uint8_t width,height; };
enum SpriteId { HeroDown0,HeroDown1,HeroUp0,HeroUp1,HeroRight0,HeroRight1,HeroLeft0,HeroLeft1,
                Skeleton0,Skeleton1,Bat0,Bat1,Slime0,Slime1,ShrineLive,ShrineClear,CandySprite,
                HomeSprite,Boss0,Boss1,SpriteCount };
extern const uint16_t Palette[16];
extern const uint8_t World[64*48];
extern const uint8_t Tiles[12][32];
extern const uint8_t TitleScene[8192];
extern const Sprite Sprites[SpriteCount];
} }
