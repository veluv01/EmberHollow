# Ember Hollow build verification

Built for WeAct CH32X035F8U6 (WF86), application origin `0x3000`. Both builds preserve two save pages.

| Build | Flash / save-safe budget | Static SRAM / budget |
|---|---:|---:|
| release | 37,140 / 50,432 B | 12,600 / 18,416 B |
| debug | 45,192 / 50,432 B | 12,968 / 18,416 B |

Base checkout: `c008a001a51f1eaa5087634193a04bbd4f0657c0`. PlatformIO 6.1.19, WCH RISC-V GCC 8.2.0, `-Os` with LTO, nano runtime.

Static SRAM includes allocated RAM code and data; the budget reserves the 16-byte boot block and 2 KB stack.

Verification: host gameplay tests and a 100,000-tick soak; two deterministic simulator runs for all three gameplay/smoke/tutorial scripts; simulated flash checkpoint/restart/continue/new-game checks; five-second exit, early release, and millisecond rollover; WF86 header, payload CRC, cover, and cart round-trip checks.

AddressSanitizer/UndefinedBehaviorSanitizer passed with leak detection disabled.

The gameplay preview is 426,400 bytes, below CHGame's 1 MB limit.

Root and game-folder PlatformIO builds are byte-identical.

The standalone repository release is also byte-identical.

**Hardware was not uploaded or tested.** 30 fps is the configured target, not a measured physical rate. Rev0 and future API releases are untested. Inspect the game folder's NOTES.md and the included logs for the check scope.
