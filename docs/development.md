# AutoStartCodex Development Notes

> Version: v1.0.6 | Updated: 2026-06-02

## Feature List

| ID  | Feature                                 | Version | Status |
|-----|-----------------------------------------|---------|--------|
| F01 | OpenAI / DeepSeek config switching      | v1.0.0  | 闂?    |
| F02 | Moon Bridge auto-compile & start        | v1.0.0  | 闂?    |
| F03 | Moon Bridge path discovery + save       | v1.0.0  | 闂?    |
| F04 | Codex auto-restart                      | v1.0.0  | 闂?    |
| F05 | Boot autostart (Registry)               | v1.0.0  | 闂?    |
| F06 | customtkinter GUI main window           | v1.0.0  | 闂?    |
| F07 | System tray (pystray)                   | v1.0.0  | 闂?    |
| F08 | Operation log panel                     | v1.0.0  | 闂?    |
| F09 | Moon Bridge source change detection     | v1.0.0  | 闂?    |
| F10 | Config file validation                  | v1.0.0  | 闂?    |
|      | **Bugfix: Codex launch priority**       | v1.0.1  | 闂?    |
|      | **Bugfix: UI double-cleanup (lag)**     | v1.0.1  | 闂?    |
|      | **Bugfix: File encoding corruption**    | v1.0.1  | 闂?    |
| F11 | PyInstaller single exe bundle           | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
| F12 | Persistent log files                    | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
| F13 | Windows notification errors             | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
|      | **Lag fix: background health check**   | v1.0.2  | 闂?    |
|      | **Close 闂?tray, Quit 闂?full exit**     | v1.0.2  | 闂?    |
|      | **Light theme + landscape layout**     | v1.0.2  | 闂?    |
|      | **Theme system (app/theme.py)**        | v1.0.2  | 闂?    |
| F11 | PyInstaller single exe bundle           | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
| F12 | Persistent log files                    | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
| F13 | Windows notification errors             | v1.1    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |
| F14 | Multi-profile visual editor             | v1.2    | 濠碘槅鍋撶徊浠嬪疮椤栫偛绠?    |

## Design Decisions

### Why customtkinter?

- Zero-compile Python dependency, no Node.js or Rust toolchain needed
- PyInstaller produces a ~15MB single exe
- Dark theme + rounded corners, looks like a native desktop app
- Easy to maintain, non-frontend developers can modify

### Moon Bridge path discovery flow

```
User clicks "Switch to DeepSeek" for the first time
  -> config.moonbridge_path is empty or invalid
  -> File dialog opens
  -> Validates: config.yml / cmd/moonbridge/ / go.mod
  -> Pass -> save path, continue
  -> Fail -> show specific missing items, re-prompt
```

### Compilation strategy

- **First run**: no moonbridge.exe -> auto compile
- **Subsequent**: compare .go source mtime vs .exe mtime
  - No change -> use exe directly, instant start
  - Source updated -> log hint, recompile
- config.yml changes do NOT affect compilation (compile and config are decoupled)

### Process management

- Moon Bridge runs as hidden background process (CREATE_NO_WINDOW)
- Health check: TCP connect to 127.0.0.1:38440
- Codex kill: `taskkill /F /IM codex.exe`
- Codex launch priority: shell command (App Execution Alias) first -> direct binary path fallback
- Autostart: Registry HKCU:\...\Run via winreg

### Config validation

- Before switching to DeepSeek: check config-deepseek.toml contains moonbridge settings
- Before switching to OpenAI: check config-openai.toml exists and has no moonbridge residual
- If missing: prompt user to configure in Codex first, then save config file

### v1.0.6 changes

- **Codex flow redesigned**: _do_switch() now checks codex.is_running()
  before starting the switch. If Codex is running and the profile is changing,
  a confirmation dialog (_ask_kill_codex) warns the user to save work, with
  "Close Codex and Switch" and "Cancel" options.
- **_switch_sync signature**: now accepts kill_codex: bool parameter.
  When True, calls self.codex.kill() then 	ime.sleep(1) before switching
  config. Never tries to auto-launch Codex.
- **After switch**: _show_manual_start_dialog() shows a messagebox.showinfo()
  telling the user to start Codex manually. This is called via self.after(0, ...)
  from the background thread.
- **Same-profile skip**: _do_switch also checks _current_profile == target.
  If already on target, calls _begin_switch_thread with kill_codex=False,
  which only manages Moon Bridge.
- **No restart**: self.codex.restart() has been completely removed. The
  codex_launcher.py launch method is preserved but no longer called from the
  switch flow.

### v1.0.5 changes

- **Tray always on**: _start_tray_async() is now called unconditionally in
  _start_gui(). The --tray flag now only controls window visibility
  (withdraw()), not tray availability. Users always get the system tray icon.
- **Stop log completeness**: _stop_moonbridge() logs both "Stopping Moon
  Bridge ..." (before) and "Moon Bridge stopped" (after the operation).
- **Left-click tray behavior**: added default=True to the "Show Window" menu
  item, so left-clicking the tray icon opens the main window, matching standard
  Windows tray conventions.
- **checked callback fix**: pystray.MenuItem.checked requires a callable that
  accepts one argument (the menu item). Changed lambda: expr to
  lambda _item: expr to fix the TypeError: takes 0 positional arguments but
  1 was given crash.

### v1.0.6 changes

- **Codex flow redesigned**: _do_switch() now checks codex.is_running()
  before starting the switch. If Codex is running and the profile is changing,
  a confirmation dialog (_ask_kill_codex) warns the user to save work, with
  "Close Codex and Switch" and "Cancel" options.
- **_switch_sync signature**: now accepts kill_codex: bool parameter.
  When True, calls self.codex.kill() then 	ime.sleep(1) before switching
  config. Never tries to auto-launch Codex.
- **After switch**: _show_manual_start_dialog() shows a messagebox.showinfo()
  telling the user to start Codex manually. This is called via self.after(0, ...)
  from the background thread.
- **Same-profile skip**: _do_switch also checks _current_profile == target.
  If already on target, calls _begin_switch_thread with kill_codex=False,
  which only manages Moon Bridge.
- **No restart**: self.codex.restart() has been completely removed. The
  codex_launcher.py launch method is preserved but no longer called from the
  switch flow.

### v1.0.5 changes

- **Tray always on**: _start_tray_async() is now called unconditionally in
  _start_gui(). The --tray flag now only controls window visibility
  (withdraw()), not tray availability. Users always get the system tray icon.
- **Stop log completeness**: _stop_moonbridge() logs both "Stopping Moon
  Bridge ..." (before) and "Moon Bridge stopped" (after the operation).

### v1.0.4 changes

- **Reader thread**: start() now spawns a daemon 	hreading.Thread that runs
  _reader_loop(), reading stdout in binary and decoding as utf-8. This never
  blocks _wait_for_ready, which now only checks TCP port and process liveness.
- **Name shadow fix**: __init__ parameter on_quit 闂?quit_callback,
  class method _on_quit() 闂?_handle_quit(). The old self._on_quit = on_quit
  was overwriting the method, so Quit button only called pp.quit() without
  stopping Moon Bridge.
- **Quit dialog**: _show_quit_dialog() opens a CTkToplevel with two buttons:
  Exit (_handle_quit) and Minimize to Tray (withdraw). 闁?button still calls
  withdraw without dialog.
- **Tray Exit**: binds to _handle_quit (direct exit, no dialog).

### v1.0.3 changes

- **GBK decode fix**: subprocess.Popen now uses binary mode (	ext=False).
  _wait_for_ready decodes eadline() output with utf-8 +
  errors='replace', never crashes on non-ASCII output.
- **Codex launch**: no longer relies on proc.wait() exit code. Uses
  is_running() (process table scan) before and after launch attempt to
  determine success.
- **Skip restart**: _switch_sync checks _current_profile == target at the
  start. If already on target and Moon Bridge needs no action, returns
  immediately. If already on DeepSeek but MB is stopped, starts MB only.
- **Launch failure dialog**: when codex.restart() returns False, UI shows a
  messagebox.showerror() asking the user to start Codex manually.
- **Stop robustness**: stop() now runs 	askkill /F /IM moonbridge.exe
  in addition to self._process.terminate(), ensuring orphan processes
  are cleaned up.

### v1.0.2 changes

- **Health check**: moved to background daemon thread with 10s interval.
  `_check_port()` TCP timeout reduced to 0.3s. Both `is_running()` and
  `health_check()` cache results for 2 seconds.
- **Close behavior**: window 闂?button calls `withdraw()` (hide to tray).
  Only explicit Quit button or tray Exit menu fully quits the app.
  Quit always stops Moon Bridge first.
- **Theme system**: `app/theme.py` exports `LIGHT` and `DARK` dicts.
  Current theme selected at the top of `ui.py` via `THEME = LIGHT`.
  All colors and fonts are driven from the theme dict 闂?changing themes
  requires a single constant swap.
- **Landscape layout**: 720x440 default, buttons at top, status + log in
  middle, controls at bottom.

## Coding Conventions

- `from __future__ import annotations` for lazy evaluation
- Full type annotations, core functions have docstrings
- Heavy operations in background threads, `after(0, ...)` for safe UI updates
- English UI strings (avoid encoding issues across platforms)
- Use `_switch_aborted` flag to prevent double-cleanup in threaded switch flow

## Build

`powershell
# Install PyInstaller
pip install pyinstaller

# Build single exe
pyinstaller --onefile --windowed --name CodexSwitch ^
  --add-data "core;core" --add-data "app;app" ^
  --hidden-import customtkinter --hidden-import pystray ^
  --hidden-import PIL --hidden-import yaml ^
  main.py

# Output: dist\CodexSwitch.exe (~24 MB)
`

Or use the generated .spec file for reproducible builds:
`powershell
pyinstaller CodexSwitch.spec
`

Build artifacts: uild/ and *.spec can be deleted after build. Only dist/CodexSwitch.exe is needed.

## Manual Test Scenarios

1. First run (no Moon Bridge path) -> prompt dialog, validation, re-prompt on failure
2. Switch to DeepSeek -> compile + start + config switch + Codex restart
3. Switch to OpenAI -> config switch + Codex restart
4. Boot autostart toggle -> verify Registry write/delete
5. System tray switching
6. Rapid double-click -> anti-repeat protection

---

> This file should be updated whenever features or architecture change.