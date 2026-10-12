# Changelog

## 1.1.0 — original-console port (2026-10-12)

- Added release and debug builds for the original CHGame Rev0 console (CH32X035G8U6 / CX35), using the same game source and save format.
- Added separate board-labeled SD and firmware downloads, a Rev0-only cart, and a combined cart containing both devices. Existing WeAct downloads remain available.
- Added application-only Rev0 PlatformIO support and CI checks for all four profiles, package reproducibility, target IDs, and wrong-board rejection.

## 1.1.0

- Added a three-page illustrated opening story introducing Wick, the six cursed shrines, and the Ash Warden. Continue bypasses it; B skips it.
- Added a numeric boss health bar and DODGE / FIRE / STRIKE cues, with a red bar at half health.
- Changed menu exit to five continuous seconds of START, with a countdown, early-release cancellation, and checkpoint before leaving play/pause.
- Added animated defeat and victory scenes, cause-specific defeat hints, time/shrine statistics, a new-best indicator, and postgame exploration with a frozen completion clock.
- Added visible parry feedback, five beginner GIF lessons, a complete gameplay reel, root PlatformIO setup, a pinned dependency, and a CI workflow.
- Extended gameplay and simulator coverage for story, save preservation, endings, and exit timing. Kept the 40-byte version-1 save format.

## 1.0.0

- Initial original Halloween/lava quest for CHGame's WeAct F8U6 port: six shrines, three creature types, guarded combat, parries, a final boss, checkpoints, and flash-resident pixel art.
