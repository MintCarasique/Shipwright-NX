![Ship of Harkinian](docs/shiptitle.darkmode.png#gh-dark-mode-only)
![Ship of Harkinian](docs/shiptitle.lightmode.png#gh-light-mode-only)

# Shipwright-NX — Ship of Harkinian for Nintendo Switch

An unofficial, Switch-only fork of [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright)
(based on **9.3.1**). Upstream dropped the Switch after 8.0.6; this fork brings it back with all current
features and a **native deko3d renderer** instead of OpenGL on Mesa.

All credit for the port itself goes to the [Harbour Masters](https://github.com/HarbourMasters). Please do
not ask them for support with this fork. The Ship does not include any copyrighted assets: you need your
own copy of the game. We do not condone piracy.

## Highlights

- **deko3d renderer**: draws go straight to the GPU, no driver in between. In Hyrule Field at stock clocks
  (1020 MHz, handheld) with 60 FPS frame interpolation: OpenGL ran at 52–55 FPS (game slowed to ~90 %),
  deko3d holds 60 FPS with about half of each frame to spare. No overclock needed.
- Shaders are generated from the same templates as on PC and compiled on the console by
  [uam](https://github.com/devkitPro/uam), then cached on the SD card.
- Native Switch integration: HOME/sleep handling, software keyboard, touch screen in the menu, controller
  buttons by label (A confirms, B goes back), docked 1080p / handheld 720p.
- CPU clocks are left to the system (or sys-clk) by default; optional profiles in
  *Settings → General → Switch Performance Mode*.

## Installation

1. Download `Shipwright-NX-<version>.zip` from [Releases](../../releases) and unpack it to the root of the
   SD card (builds of every commit are also in the [Actions](../../actions) artifacts):
   ```
   sdmc:/switch/soh/soh.nro
   sdmc:/switch/soh/soh.o2r
   ```
2. Create `oot.o2r` (and/or `oot-mq.o2r`) from your ROM with the **PC version of SoH 9.3.1**
   ([download](https://github.com/HarbourMasters/Shipwright/releases/tag/9.3.1)) and copy it next to
   `soh.nro`. ROM extraction is not available on the Switch. You can check your dump at
   https://ship.equipment/.
3. Launch from the Homebrew Menu (or sphaira) in **full-memory mode**: hold R while starting any game.
   Applet mode (from the Album) is not supported.

On the first run, every new shader is compiled once (30–100 ms each) and cached in
`sdmc:/switch/soh/cache/dksh/`, so new areas may stutter briefly the first time only.

## Controls

- **−** opens and closes the SoH menu. Navigate with the D-pad (A select, B back) or the touch screen.

## Versions

Versions follow upstream Ship of Harkinian, with our build number after a dash: `9.3.1-1`, `9.3.1-2`, ...
The number restarts at 1 when the fork moves to a new upstream release. Pushing a tag in that form makes
CI build it and publish a release (the tag must match the version in `CMakeLists.txt`).

## Building

Requirements: Docker (for devkitA64) and a host compiler with CMake, Ninja, zlib, bzip2 and libpng
(for the asset tools).

```bash
git clone --recursive https://github.com/MintCarasique/Shipwright-NX.git
cd Shipwright-NX
tools/switch/build.sh configure
```

Outputs: `build-switch/soh/soh.nro` and `build-host/soh/soh.o2r`. CI (`.github/workflows/switch.yml`) does
the same and packages the SD card layout.

The renderer and platform code live in the [libultraship-nx](https://github.com/MintCarasique/libultraship-nx)
fork (branch `switch`), included here as the `libultraship` submodule.

## Debugging over nxlink

Launch with nxlink in server mode, e.g. `nxlink -a <switch ip> -p soh/soh.nro -s soh.nro`. While connected
the game streams:

- its log, plus one `[prof]` / `[gl]` line per second (FPS, game logic / render / swap time, audio buffer,
  CPU/GPU/EMC clocks);
- a screenshot every 15 seconds — `python tools/switch/nxlink_screens.py live.log` turns them into PNGs;
- on a crash, a `[crash]` block with module-relative addresses; symbolize them with
  `aarch64-none-elf-addr2line -f -C -e soh.elf <offset>` (the CI uploads `soh.elf`).

Without nxlink all of this is off.

## Known limitations

- OpenGL is not available on the Switch build: uam's copy of Mesa and switch-mesa's libEGL cannot coexist.
- MSAA is not implemented.

## License

Same as upstream Ship of Harkinian and libultraship. uam (`libultraship/extern/uam`) is zlib (its own
files) and MIT (`mesa-imported/`).
