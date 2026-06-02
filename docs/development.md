# CodexSwitch Development Notes

> Version: v1.0.2 | Updated: 2026-06-02

## Design Decisions

### Why customtkinter?

- Zero-compile Python dependency, no Node.js or Rust toolchain needed
- PyInstaller produces a ~15MB single exe
- Dark theme + rounded corners, looks like a native desktop app
- Easy to maintain, non-frontend developers can modify

### Moon Bridge path discovery flow

User clicks "Switch to DeepSeek" for the first time:
  1. Check config.moonbridge_path
  2. If empty/invalid -> file dialog opens
  3. Validate: config.yml / cmd/moonbridge/ / go.mod
  4. Pass -> save path, continue
  5. Fail -> show specific missing items, re-prompt

### Compilation strategy

- First run: no moonbridge.exe -> auto compile
- Subsequent: compare .go source mtime vs .exe mtime
  - No change -> use exe directly, instant start
  - Source updated -> log hint, recompile
- config.yml changes do NOT affect compilation (decoupled)

### Process management

- Moon Bridge: hidden background process (CREATE_NO_WINDOW)
- Health check: TCP connect to 127.0.0.1:38440 (0.3s timeout)
  Runs in background daemon thread (10s interval), cached 2 seconds
- Codex kill: taskkill /F /IM codex.exe
- Codex launch: shell command (App Execution Alias) first, binary fallback

### Config validation

- Before DeepSeek: check config-deepseek.toml contains moonbridge settings
- Before OpenAI: check config-openai.toml has no moonbridge residual
- If missing: prompt user to configure in Codex first, then save config file

### Switch flow (v1.0.1)

User clicks Switch to X:
  1. Check if already on target profile (skip if yes)
  2. Check Codex running status via tasklist
  3. If running + profile changing -> show kill confirmation dialog
     - Confirm: kill Codex, switch config, prompt manual start
     - Cancel: abort
  4. If not running -> switch config, prompt manual start

No auto-launch. User always starts Codex manually after switch.

### Quit flow (v1.0.1)

- Window close (x): withdraw() to tray, Moon Bridge keeps running
- Quit button: dialog with Exit (stop MB + quit) or Minimize to Tray
- Tray Exit: direct quit, stops MB, no dialog

### Theme system (v1.0.1)

app/theme.py exports LIGHT and DARK dicts. All colors and fonts driven
from theme. Current theme selected at top of ui.py via THEME = LIGHT.

### Encoding (v1.0.1)

All source files must be UTF-8 without BOM. Use PowerShell:
```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

### Moon Bridge stdout reader thread (v0.9)

`_wait_for_ready` originally blocked on `readline()` waiting for stdout output.
Fixed by moving stdout reading to a background daemon thread (`_reader_loop`),
so `_wait_for_ready` only polls TCP port and process status — never blocks.

### Quit callback naming (v0.9)

Instance attribute `self._on_quit` was shadowing the `_on_quit()` method.
Renamed to `self._quit_callback` and `_handle_quit()`. Quit now always
stops Moon Bridge first.

## Coding Conventions

- `from __future__ import annotations` for lazy evaluation
- Full type annotations, core functions have docstrings
- Heavy operations in background threads, `after(0, ...)` for safe UI updates
- English UI strings (avoid encoding issues)
- Use `_switch_aborted` flag to prevent double-cleanup in threaded switch flow
  (e.g. when Moon Bridge path is not set during switch, abort flag prevents
   conflicting state resets from switch logic and error handlers)

## Manual Test Scenarios

1. First run (no Moon Bridge path) -> prompt dialog, validation, re-prompt
2. Switch to DeepSeek -> compile + start + config switch + prompt Codex start
3. Switch to OpenAI -> config switch + prompt Codex start
4. Boot autostart toggle -> verify Registry write/delete
5. System tray: left-click show window, right-click menu
6. Quit dialog: Exit vs Minimize to Tray
7. Stop Moon Bridge button -> verify port closed
8. Rapid double-click -> anti-repeat protection

## Build

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

Using spec file (recommended):
```powershell
pyinstaller CodexSwitch.spec --clean
```

Or command line:
```powershell
pyinstaller --onefile --windowed --name CodexSwitch-1.0.2-amd64 ^
  --add-data "core;core" --add-data "app;app" --add-data "assets;assets" ^
  --icon "assets\icons\arrow.ico" main.py
```

Output: `dist\CodexSwitch-<version>-<arch>.exe`

### Dynamic version naming

The executable name is generated dynamically from `core/__version__` and
`platform.machine().lower()`, producing e.g. `CodexSwitch-1.0.2-amd64.exe`.

The spec file imports the version at build time via:
```python
sys.path.insert(0, SPECPATH)
from core import __version__
```

### Icon assets

| Asset | Purpose | Format |
|-------|---------|--------|
| `assets/icons/arrow.ico` | EXE icon + window taskbar icon | ICO (multi-res: 16/32/64/128/256) |
| `assets/icons/arrow_tray.png` | System tray icon (pystray) | PNG, 64×64 RGBA |

- ICO file is embedded via `icon=` in `EXE()` within the spec file.
- Window taskbar icon is set via `self.iconbitmap()` in `app/ui.py`.
- Tray icon is loaded from `arrow_tray.png` in `app/tray.py`.
- All asset paths use `_resource_path()` / `_tray_icon_path()` helpers that
  resolve correctly both in development (`__file__`-relative) and in the
  PyInstaller bundle (`sys._MEIPASS`-relative).

### Resource path resolution

When accessing bundled files (icons, configs, etc.), always use a helper to
handle the path difference between development and PyInstaller bundle mode:

```python
import os
import sys

def resource_path(relative: str) -> str:
    """Get absolute path, works in dev and PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', relative)
```
