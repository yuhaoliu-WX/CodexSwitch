# CodexSwitch Architecture

> Version: v1.0.6 | Updated: 2026-06-02

## Overview

CodexSwitch is a Windows desktop tool for switching Codex configurations
between OpenAI and DeepSeek (via Moon Bridge), and managing the Moon Bridge
process lifecycle.

## Project structure

```
CodexSwitch/
+-- main.py                  # Entry point
+-- requirements.txt         # Python dependencies
+-- CodexSwitch.spec         # PyInstaller build config
|
+-- core/                    # Business logic
|   +-- models.py            # Data models and enums
|   +-- config_manager.py    # Config persistence + registry autostart
|   +-- config_switcher.py   # Codex config file switching
|   +-- moon_bridge.py       # Compile, start, stop, health check
|   +-- codex_launcher.py    # Find, kill Codex process
|
+-- app/                     # GUI layer
|   +-- theme.py             # Theme system (LIGHT / DARK)
|   +-- ui.py                # customtkinter main window
|   +-- tray.py              # System tray (pystray)
|
+-- docs/
|   +-- architecture.md      # This file
|   +-- development.md       # Development notes
|
+-- logs/
    +-- changelog.md         # Version changelog
```

## Architecture layers

### Core layer (core/)

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| models.py | Enums, dataclasses | None |
| config_manager.py | Load/save config.yaml, registry autostart | PyYAML, winreg |
| config_switcher.py | Copy profile .toml to config.toml | None |
| moon_bridge.py | Path validation, compilation, process mgmt, TCP health | Go compiler |
| codex_launcher.py | Find codex.exe, kill via taskkill, process table check | None |

### GUI layer (app/)

| Module | Framework | Responsibility |
|--------|-----------|---------------|
| ui.py | customtkinter | Main window: status, buttons, log, settings |
| tray.py | pystray | System tray right-click menu |
| theme.py | - | LIGHT / DARK theme dicts, font constants |

## Key flows

### Switch to DeepSeek

```
User clicks "Switch to DeepSeek"
  -> Check Moon Bridge path configured (prompt if not)
  -> Check moonbridge.exe exists (compile if not / source changed)
  -> Start moonbridge.exe (CREATE_NO_WINDOW, hidden)
  -> Poll 127.0.0.1:38440 until ready
  -> Check Codex running status
    -> If running: show kill confirmation dialog
      -> User confirms: kill Codex, switch config, prompt manual start
      -> User cancels: abort
    -> If not running: switch config, prompt manual start
  -> Update UI state
```

### Switch to OpenAI

```
User clicks "Switch to OpenAI"
  -> Check config-openai.toml exists
  -> Same Codex running flow as above
  -> Switch config, prompt manual start
  -> Moon Bridge stays running (optional)
```

## Key design decisions

### Theme system

All colors and fonts are driven from theme dicts in app/theme.py.
Change LIGHT to DARK in ui.py to switch themes.

### Health check

Moon Bridge TCP check runs in a background daemon thread (10s interval).
Results are cached for 2 seconds. Never blocks the UI thread.

### Process management

- Moon Bridge: hidden background process (CREATE_NO_WINDOW)
- Health check: TCP connect to 127.0.0.1:38440 (0.3s timeout)
- Codex kill: taskkill /F /IM codex.exe
- Codex launch: shell command (App Execution Alias) first, binary fallback

### Quit flow

| Action | Behavior |
|--------|----------|
| Window close (x) | withdraw() to tray, Moon Bridge keeps running |
| Quit button | Dialog: Exit (stop MB + quit) or Minimize to Tray |
| Tray Exit | Direct quit, no dialog, stops MB |

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | >= 3.10 | Runtime |
| customtkinter | >= 5.2 | GUI |
| pystray | >= 0.19 | System tray |
| Pillow | >= 10 | Tray icon |
| PyYAML | >= 6 | Config |
| Go | >= 1.21 | Moon Bridge compilation |

## FAQ

### VPN and DeepSeek

See README.md VPN note. In short: VPN ON to start Codex (for OpenAI),
VPN OFF when using DeepSeek (domestic API, direct connection is stable).

### Where is the config file?

C:\Users\<username>\.codex-switcher\config.yaml
Auto-generated on first run. All settings managed via GUI.

### How to fully exit?

Click Quit button -> select Exit, or tray right-click -> Exit.
Both stop Moon Bridge before quitting.
