# AutoStartCodex Changelog

## v1.0.6 (2026-06-02)

### Changed

- **Codex auto-launch removed**: automatic Codex launch never reliably worked
  with the Windows App Store version. After switching config, the tool now
  prompts the user to start Codex manually via a dialog.
- **Switch flow redesigned**:
  1. Before switching profiles, checks if Codex is currently running
  2. If running + profile is changing 鈫?shows confirmation dialog asking user
     to save work before closing Codex
  3. If user confirms 鈫?closes Codex, switches config, prompts manual start
  4. If Codex is not running 鈫?switches config directly, prompts manual start
  5. If already on target profile 鈫?only manages Moon Bridge, no Codex action

### Added

- **Codex status check**: `_do_switch()` now checks `codex.is_running()` before
  any operation. No assumptions about Codex state.
- **Kill confirmation dialog**: when Codex is running and profile needs to
  change, a `CTkToplevel` dialog warns the user to save work, with "Close Codex
  and Switch" / "Cancel" buttons.
- **Manual start prompt**: after config is switched, `_show_manual_start_dialog()`
  shows an info dialog telling the user to start Codex manually.

### Removed

- `_switch_sync` no longer calls `self.codex.restart()`. All Codex launch logic
  removed. Kill logic kept and only runs when user confirms.

### Build

- **First release build**: `CodexSwitch.exe` (23.7 MB) built with PyInstaller
  6.20.0, located in `dist/`. Single-file portable executable, no dependencies.
  Run with: `dist\CodexSwitch.exe`

- `_switch_sync` no longer calls `self.codex.restart()`. All Codex launch logic
  removed. Kill logic kept and only runs when user confirms.

## v1.0.5 (2026-06-02)

### Fixed

- **Stop Moon Bridge log**: `_stop_moonbridge()` now logs "Moon Bridge stopped"
  after the stop completes, so the log shows both starting and stopped messages.
- **Tray icon always present**: the system tray icon now starts regardless of
  whether `--tray` is passed. `--tray` only controls whether the window is
  initially hidden. Previously `--tray` was required to get the tray at all.
- **Tray left-click not responding**: `pystray.MenuItem.checked` callbacks must
  accept one positional argument (the menu item). Changed `lambda: ...` to
  `lambda _item: ...`. Also added a `default=True` menu item so left-click
  shows the window.
- **Tray text encoding**: fixed corrupted Chinese characters in tray menu
  (replaced with English strings).

### Added

- **Left-click tray icon**: now shows the main window (via `default=True`
  menu item), matching standard Windows tray behavior.

## v1.0.4 (2026-06-02)

### Fixed

- **Stop Moon Bridge log**: `_stop_moonbridge()` now logs "Moon Bridge stopped"
  after the stop completes, so the log shows both starting and stopped messages.
- **Tray icon always present**: the system tray icon now starts regardless of
  whether `--tray` is passed. `--tray` only controls whether the window is
  initially hidden. Previously `--tray` was required to get the tray at all.

## v1.0.4 (2026-06-02)

### Fixed

- **Moon Bridge re-connect hang**: after Stop then Start, `_wait_for_ready`
  was blocking on `readline()` waiting for stdout output. Moved stdout reading
  to a background daemon thread (`_reader_loop`), so `_wait_for_ready` only
  polls TCP port and process status 闂?never blocks.
- **Quit not stopping Moon Bridge**: instance attribute `self._on_quit` was
  shadowing the `_on_quit()` method. Renamed to `self._quit_callback` and
  `_handle_quit()`. Quit now always stops Moon Bridge first.

### Added

- **Quit dialog**: clicking Quit shows a custom dialog with two choices:
  "Exit" (stop MB + quit) or "Minimize to Tray" (withdraw).
  Window close button (闁? still withdraws silently 闂?no dialog.
- **System tray Exit**: right-click 闂?Exit in tray directly calls
  `_handle_quit()` (stop MB + quit), no dialog.

### Changed

- Tray on_quit callback now points to `app._handle_quit` instead of `app.quit`

## v1.0.3 (2026-06-02)

### Fixed

- **GBK decode crash**: Moon Bridge process output was using `text=True` in
  `subprocess.Popen`, which on Chinese Windows defaults to GBK and crashes on
  UTF-8 output. Changed to binary read + `utf-8` decode with `errors="replace"`.
- **Codex launch failure**: The `codex` shell command returns exit code 1 when
  Codex is already running. Changed launch logic to check process table
  (`tasklist`) instead of exit code. Only reports failure after confirming the
  process never appeared.
- **Moon Bridge stop reliability**: `stop()` now runs `taskkill /F /IM
  moonbridge.exe` by process name in addition to terminating the tracked
  process. Waits for port to close before returning. Clears health check cache
  so next status read is fresh.

### Added

- **Skip restart on same profile**: clicking "Switch to DeepSeek" while already
  on DeepSeek now only manages Moon Bridge (start if stopped), without touching
  config or restarting Codex.
- **Codex launch failure dialog**: if auto-launch fails, a messagebox prompts
  the user to start Codex manually, instead of silently reporting success.

## v1.0.2 (2026-06-02)

### Fixed

- **GUI lag**: removed all TCP socket checks from the tkinter main thread.
  Moon Bridge health check now runs in a dedicated daemon thread with a 10s
  interval. Added 2-second result cache so `is_running()` and `health_check()`
  return cached data without blocking.
- **Close behavior**: window close button now hides to system tray (withdraw)
  instead of quitting. Moon Bridge keeps running in background.

### Added

- **Quit button**: fully exits the app and stops Moon Bridge process
- **Stop Moon Bridge button**: stops the Moon Bridge process without quitting
- **Landscape layout**: window resized from 520x640 to 720x440
- **Light theme**: default theme is now white/light. Theme system extracted
  into `app/theme.py` with `DARK` and `LIGHT` dicts; switching themes is a
  one-line change.
- **Background health check**: periodic Moon Bridge status checking moved to
  a background daemon thread, never blocking UI events.

### Changed

- `MainWindow.__init__` now requires `on_quit` callback parameter
- `app/theme.py` added as new module for centralized style management

## v1.0.1 (2026-06-02)

### Fixed

- **Codex launch**: fixed the launch priority to use `codex` shell command first
  (App Execution Alias) instead of the direct binary path, which was being blocked
  by WindowsApps permission restrictions
- **UI threading**: fixed double-cleanup bug when Moon Bridge path is not set.
  Added `_switch_aborted` flag to prevent conflicting state resets
- **UI text encoding**: replaced all Chinese strings with English to avoid
  encoding corruption across file writes

### Changed

- Moon Bridge now runs as a hidden background process (`CREATE_NO_WINDOW`)
  instead of requiring a visible PowerShell window to stay open

## v1.0.0 (2026-06-02)

### Features

- **F01** OpenAI / DeepSeek config switching: one-click switch, auto-backup
- **F02** Moon Bridge auto-management: path detection, compilation, start, health check
- **F03** Moon Bridge path discovery: first-use dialog with validation, persistent save
- **F04** Codex auto-restart: kill and re-launch after config switch
- **F05** Boot autostart: Windows Registry, toggle in GUI
- **F06** GUI main window: customtkinter dark theme, status, buttons, log, settings
- **F07** System tray: pystray right-click menu for quick switching
- **F08** Operation log panel: real-time log inside the GUI
- **F09** Source change detection: recompile moonbridge.exe when .go files are newer
- **F10** Config validation: check target config file exists and is well-formed

### Tech stack

- Python 3.12 + customtkinter 5.2 + pystray 0.19 + PyYAML 6 + Pillow 10
- Go 1.26 (Moon Bridge compilation)
- Windows Registry (autostart)
