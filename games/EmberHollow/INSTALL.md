# Install Ember Hollow on CHGame

The game supports two consoles from one source. Choose your target before copying or uploading firmware.

| Console | Device name / target | Repository SD download | Release / debug environments |
|---|---|---|---|
| Original CHGame Rev0, CH32X035G8U6 | `rev0` / CX35 | `sdcard/rev0/GAMES/EMBER.CHG` | `ember-rev0` / `ember-rev0-debug` |
| WeAct CH32X035F8U6 variant | `weact-f8u6` / WF86 | `sdcard/weact-f8u6/GAMES/EMBER.CHG` | `ember` / `ember-debug` |

Both builds use the board's existing 128×128 display and eight-button mapping. All art is embedded; no `.DAT` file is needed. The game is silent on both boards. The original console uses its standard hardware with no wiring changes.

## Play from the SD menu

1. Download the **EMBER.CHG for your console** from the table above.
2. Copy it into the existing SD card's `GAMES/` folder as `EMBER.CHG`, keeping your other games and menu files.
3. Safely eject the card, return it to the console, and restart.
4. Select **EMBER HOLLOW** in the installed CHGame menu and press A.

Both list and visual menus can launch the game; each package includes the cover image. The legacy `sdcard/GAMES/EMBER.CHG`, `firmware/EmberHollow.bin`, and `cart/EmberHollow.chgame` are still **WeAct-only**. Renaming a firmware file does not change its board target.

Hold START continuously for **five seconds** to save play/pause progress and return to the SD menu. A countdown appears after half a second; release early to cancel. This works on every screen. It requires the compatible CHGame SD-menu bootloader already installed on that console.

## Build with PlatformIO

Install Git and Python 3.10+, then run from the repository root:

```sh
python -m pip install -r tools/requirements.txt
python tools/project.py setup
# Original CHGame console:
pio run -e ember-rev0
# WeAct variant:
pio run -e ember
```

Setup fetches the dependency revision in `dependency-lock.json`. The builds use the unmodified Arduino core, libraries, and board variants from that checkout. After setup, open the repository root in VS Code / PlatformIO and select the appropriate environment.

To use an existing compatible checkout instead of downloading it:

```sh
python tools/project.py setup --source /path/to/CHGame
```

Alternatively, copy `games/EmberHollow` into the maintained CHGame fork and open that game folder in PlatformIO; its configuration exposes the same four environments. The game-local Rev0 adapter reads the original console's variant and does not require editing the shared core.

## Upload through USB

For an original Rev0 console:

```sh
pio run -e ember-rev0 -t upload --upload-port COM5
```

For the WeAct variant:

```sh
pio run -e ember -t upload --upload-port COM5
```

Replace `COM5` with the actual port, for example `/dev/ttyACM0`. Upload uses the existing CHGame USB bootloader and checks the device identity. These environments write applications at `0x3000`; they do not provision or replace bootloaders. A working SD-menu console only needs the `.CHG` copy above.

Use `ember-rev0-debug` or `ember-debug` for serial debug builds. Exported files appear under `games/EmberHollow/build/<device>/release/` or `debug/`. Both debug profiles retain the complete game and saving.

## Regenerate downloads and carts

From the repository root:

```sh
python tools/project.py build
python games/EmberHollow/tools/package_boards.py
python games/EmberHollow/tools/package_boards.py --check
```

If you built from the game folder instead, add `--build-root games/EmberHollow` to the packaging commands run from the root.

`build` compiles all four environments. Packaging writes board-labeled `.bin` and `.CHG` files, a Rev0-only cart, and `cart/EmberHollow-MultiBoard.chgame` with both binaries. The check verifies each target, payload, menu picture, wrong-board rejection, and cart round trip. Legacy WeAct downloads remain untouched.

To prepare a card from the combined cart using CHGame tools:

```sh
python tools/chgame.py cart prepare cart/EmberHollow-MultiBoard.chgame out/card-rev0 --device rev0
python tools/chgame.py cart prepare cart/EmberHollow-MultiBoard.chgame out/card-weact --device weact-f8u6
```

Copy the generated card contents to the matching console's card. A `.chgame` is a distributable cart read by desktop/web tools; the hardware SD menu installs `.CHG` files.

## Updates and saves

Both builds retain the `EHLO` magic and version-1, 40-byte save format from Ember Hollow 1.0. Story and animation state remain transient. Saves live in each console's flash; using the same SD card does not transfer your checkpoint between consoles.

CHGame titles share two flash save pages. Another game's save can replace Ember Hollow's checkpoint. NEW resets the current quest while retaining the best completion time; opening the intro alone does not erase the old checkpoint.

After updating the dependency, rebuild all four profiles, run the checks, and regenerate the packages. Future API compatibility requires those checks. See `BUILD_REPORT_BOARDS.md` at the repository root for measured sizes and scope. Physical hardware uploads, TFT timing, and gameplay feel have not been tested here.
