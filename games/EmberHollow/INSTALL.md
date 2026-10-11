# Install Ember Hollow on CHGame / WeAct F8U6

This package targets **WeAct CH32X035F8U6**, the existing 128x128 ST7735S display, and the eight-button CHGame wiring. Its firmware target is **WF86**, not the original Rev0 board's CX35. It uses the board's existing silent audio/LED variant and leaves its debug pins available.

## Play from the SD menu

1. Unzip the package.
2. Copy `sdcard/GAMES/EMBER.CHG` into the existing SD card's `GAMES/` folder. Keep your other games and menu files.
3. Safely eject the card, return it to the handheld, and restart.
4. Select **EMBER HOLLOW** in the CHGame menu and press A to install/start it.

The package includes its visual-menu cover. Both list and visual WeAct menu bootloaders can launch it. All game art is inside the firmware; there is no `.DAT` file to copy. The `.chgame` file is a distributable cart for CHGame tools, while the `.CHG` file is the program the hardware SD menu installs.

Hold START continuously for **five seconds** to return to the SD menu. A countdown appears after half a second; release early to cancel. This works on the title, story, play, pause, and ending screens. Returning to the SD menu requires the compatible WeAct menu bootloader already installed on the handheld.

## Open the standalone repository

The distribution root is also a PlatformIO project. Install Python 3.10 or later and Git, then run these commands at the distribution root:

```sh
python -m pip install -r tools/requirements.txt
python tools/project.py setup
pio run -e ember
```

Setup fetches the dependency revision recorded in `dependency-lock.json` and imports its unchanged core, tools, and WeAct port into ignored local folders. After setup, open the distribution root in VS Code / PlatformIO. Use `ember-debug` for the serial debug protocol. To use an existing compatible CHGame checkout, run `python tools/project.py setup --source /path/to/CHGame` instead.

For a first installation on this already working handheld, copying the `.CHG` to the SD card is sufficient; rebuilding is optional.

## Develop inside CHGame

Use a CHGame checkout with the maintained `ports/weact-f8u6` integration. The builds supplied here were made against [this CHGame fork](https://github.com/veluv01/CHGame) at commit `c008a001a51f1eaa5087634193a04bbd4f0657c0`.

1. Copy the package's `games/EmberHollow` folder to `<CHGame checkout>/games/EmberHollow`.
2. In VS Code / PlatformIO, open **that game folder** as the project. Its `platformio.ini` refers to the core, variant, libraries, and builder in the parent checkout.
3. Select the `ember` environment and use Build or Upload.

From a terminal in the CHGame repository root:

```sh
pio run -d games/EmberHollow -e ember
pio run -d games/EmberHollow -e ember -t upload --upload-port COM5
```

Replace `COM5` with the handheld's serial port, such as `/dev/ttyACM0` on Linux. Upload uses the existing CHGame USB bootloader. It builds and writes the application; bootloader replacement and factory-ISP provisioning are not needed for an already working handheld.

The exported release files are under `games/EmberHollow/build/weact-f8u6/release/`. For the serial debug protocol:

```sh
pio run -d games/EmberHollow -e ember-debug
```

Debug exports go to `build/weact-f8u6/debug/`. Both environments keep saving, map/help screens, and the complete game. No sound hardware is required.

## Rebuild the packaged SD game

After building, run the following from the CHGame repository root with the CHGame tools' Python dependencies installed:

```sh
python tools/chgpack.py pack games/EmberHollow/build/weact-f8u6/release/EmberHollow.ino.bin EMBER.CHG --title "EMBER HOLLOW" --version 1.1.0 --image games/EmberHollow/docs/cart.png --device weact-f8u6
python tools/chgame.py --sketch games/EmberHollow export --no-build --device weact-f8u6
```

Only the `EMBER.CHG` from the first command belongs in the hardware card's `GAMES/` folder. The export command writes `build/weact-f8u6/EmberHollow.chgame` for sharing or deploying with CHGame's cart tools.

## Upstream updates and saves

The game includes no copied core, library, pin map, or SD-streaming extensions. Keep it under `games/EmberHollow` when updating the parent CHGame fork, rebuild, and run its tests. Compatibility with future API changes requires those checks; the package does not claim to be tested against unreleased versions.

Version 1.1 keeps the 40-byte, version-1 save format from 1.0; the story and ending animation state is temporary.

Each CHGame game shares the same two flash save pages. Ember Hollow uses the unique magic `EHLO`, save version 1, so another game's record is ignored. Playing a different game can replace Ember Hollow's checkpoint when that game saves. Ember Hollow's NEW option resets its current quest while retaining its best time.

The included build report records compilation and simulator checks. Physical TFT transfer time, button feel, actual frame rate, and flash endurance were not measured on hardware.

