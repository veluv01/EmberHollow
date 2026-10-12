# Both-board build report

Ember Hollow 1.1.0 uses one game source for the original CHGame Rev0 and the WeAct F8U6 variant.

| Board | Profile | Flash / save-safe budget | Static SRAM / budget |
|---|---|---:|---:|
| weact-f8u6 | release | 37,140 / 50,432 B | 12,600 / 18,416 B |
| weact-f8u6 | debug | 45,192 / 50,432 B | 12,968 / 18,416 B |
| rev0 | release | 37,188 / 50,432 B | 12,600 / 18,416 B |
| rev0 | debug | 45,224 / 50,432 B | 12,968 / 18,416 B |

Both targets use application origin `0x3000`, reserve two 256-byte save pages, and keep the version-1, 40-byte EHLO save record. Static SRAM includes RAM-resident code; the budget reserves the retained 16-byte boot block and 2 KB stack.

Rev0 selects the upstream `CHGame_Rev0` variant, CH32X035G8U chip definition, and CX35 target (`0x35335843`). WeAct selects `CHGame_WeActF8U6`, CH32X035F8U, and WF86 (`0x36384657`).

The package checker validates each builder CHG and release CHG, payload CRC, visual-menu picture, wrong-board rejection, and both the Rev0-only and combined carts. CI rebuilds all four profiles and compares these packages with the committed files.

Shared gameplay, save/restart, story, endings, five-second exit, and deterministic rendering are covered by the simulator checks. Board-specific wiring and electrical timing require a real console.

**No hardware upload or playtest was performed.** The 30 Hz frame rate and 12 MHz display clock are configuration values, not measured performance.

Dependency: `c008a001a51f1eaa5087634193a04bbd4f0657c0`. PlatformIO 6.1.19, pinned WCH RISC-V GCC 8.2, `-Os` and LTO.
