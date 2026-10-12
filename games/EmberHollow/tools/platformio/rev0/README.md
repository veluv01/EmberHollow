# Original-console PlatformIO adapter

This application-only platform selects the released CHGame Rev0 console: CH32X035G8U6, the upstream `CHGame_Rev0` variant, and target CX35 (`0x35335843`). The game code and generated artwork are shared with the WeAct build.

Use `ember-rev0` or `ember-rev0-debug` from the repository root or game folder after setup. The WeAct environments continue to use the dependency's existing platform directly.

## What is maintained here

- `platform.py` selects the same pinned WCH GCC 8 toolchains as the maintained WeAct platform. Its selection logic is adapted from that Apache-2.0 source.
- `boards/rev0.json` supplies PlatformIO's board identity and the `ARDUINO_CHGAME_REV0` macro. It does not include WeAct or debug-pin-lock macros.
- `builder/rev0_profile.py` reads current `rev0.*` settings from the dependency's Arduino `boards.txt`, applies the sketch and environment options, and rejects an unexpected variant, chip, ABI, or linker memory map.
- `builder/main.py` adapts the dependency's application build mechanics. It compiles the original core/variant directly, reserves the game's save pages, writes CX35 packages, and sends USB uploads with `--device rev0`.

No Arduino core, peripheral library, pin map, or game logic is copied into this adapter. It refuses bootloader builds. Application origin remains `0x3000`; two save pages leave a 50,432-byte flash budget and the static SRAM budget is 18,416 bytes.

## Dependency updates

Read the upstream board and build changes before changing the lock. Review this adapter when the Arduino recipes, board properties, compiler, or memory layout change. Rebuild all four game environments, run the simulator checks, and run `tools/package_boards.py --check` from the game folder (or its full path from the root). CI verifies the generated release packages and rejects a package targeted at the opposite board.

The build integration and packaged firmware have been compiled and checked in software. No physical Rev0 console was uploaded or playtested during this port.
