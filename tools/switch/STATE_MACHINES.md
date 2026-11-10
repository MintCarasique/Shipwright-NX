# State machines of the Switch port

The port-specific code keeps a handful of small state machines. Each one is a single enum next to
the code that drives it. This file is the map: what the states are, what moves them, and where to
look in a log.

Transitions of the platform machines are logged as `[state] <machine>: <from> -> <to>`, both to the
SD card log and to nxlink, so `grep "\[state\]" live.log` gives the port's view of a session.

## Platform layer (`libultraship/src/ship/port/switch/SwitchImpl.cpp`)

| Machine | States | Moved by |
| --- | --- | --- |
| `Lifecycle` | `Boot -> PreInit -> Running -> Exited` | `Switch::Init(PreInitPhase)` from `InitOTR`, `Init(PostInitPhase)` from the SDL window, `Switch::Exit` from the window's `Destroy`. Init and Exit are safe to repeat. |
| `ClockState` | `Untouched`, `Pinned`, `Yielded` | `Switch::ApplyOverclock` (menu, start-up, performance-mode change), focus changes, `Exit`. |
| `KeyboardState` | `Unknown`, `Hidden`, `Shown` | `Switch::ImGuiProcessEvent`, from ImGui's `WantTextInput`. |
| `NetLogState` | `NotStarted`, `Offline`, `Connected`, `Lost` | `StartNetLog` once at start-up; any failed write moves `Connected -> Lost`. The profiler runs only while `Connected`. |

Rules of the CPU clock machine, which is the one that matters to players:

- `Untouched` is the default ("System Default" in the menu). The game never writes a clock, so
  sys-clk and HOS stay in charge.
- A menu choice other than System Default pins the clock: `Untouched -> Pinned`.
- Losing focus hands the CPU back at stock (`Pinned -> Yielded`); regaining it pins again. A
  performance-mode change (dock / undock) while in the background does not re-pin.
- Choosing System Default again, or exiting, restores stock once and returns to `Untouched`. Stock
  is only written if the game is the one that changed the clock.
- A clock write that fails does not change the state.

Also logged, without being machines of their own: `[state] focus: ...`, `[state] display: docked |
handheld`, `[state] lifecycle: exit requested`.

## Renderer (`libultraship/src/fast/backends/gfx_deko3d.cpp`)

| Machine | States | Notes |
| --- | --- | --- |
| `FramePhase` | `Idle -> Recording -> Idle`, `Idle -> Immediate -> Idle` | `Recording` is `StartFrame..EndFrame`. `Immediate` is a read-back (pixel depth, framebuffer to CPU) asked for between frames. |
| `Barrier` | `None < Fragments < Full` | The barrier owed before the next draw. A stronger request replaces a weaker one. |
| `ImGuiState` | `Uninitialized -> Ready` or `-> Failed` | Resources are created on the first ImGui draw. `Failed` is final. |
| `ShaderCompiler::Job` | `Idle -> Queued -> Compiling -> Done -> Idle` | One job slot; the render thread blocks in `Get` until `Done`. |

What each frame phase allows:

| | `Idle` | `Recording` |
| --- | --- | --- |
| Draws, clears, framebuffer copies | ignored | recorded |
| Texture upload | queued, done at the next `StartFrame` (dropped if the texture was deleted meanwhile) | recorded |
| Image descriptor write | straight to memory | push-data command |
| Barrier | stays owed until the next frame | emitted |
| Replacing an image a recent draw sampled | waits for the GPU | barrier first |
| Swapchain resize (dock / undock) | done | deferred to the next frame |

When adding a renderer entry point that records commands, start it with `if (!Recording()) return;`
or give it an `Idle` behaviour from the table.

Texture slots have a lifecycle too (free, allocated, has an image, pending free); it is described
above `struct TextureDk` and is still tracked with flags.

## Left as they are

These are implicit but small, local and correct; changing them would add risk for no gain.

- Profiler window (`SwitchProf::FrameEnd`): static locals, `windowStart == 0` means "not primed".
- Controller slots (`ControlDeck::WriteToOSContPad`): `sLastSlots == UINT32_MAX` means "first poll".
- Net screenshots (`EndFrame`): a 15 s timer in a static.
- SDL window backend (`gfx_sdl2.cpp`): `mUseDeko3d` / `mCtx` / `mRenderer` select deko3d, OpenGL or
  Metal; only deko3d is reachable on the Switch.
- Archive check at start-up (`OTRGlobals::RunExtract`): already explicit upstream
  (`ExtractSteps`, `PromptSteps`); on the Switch it only verifies.
