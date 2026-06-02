# CodexSwitch

One-click switch Codex config, auto-manage Moon Bridge process.

---

## Background

The [official Codex + DeepSeek guide](https://github.com/deepseek-ai/awesome-deepseek-agent/blob/main/docs/codex.zh-CN.md) walks through setting up Codex with Moon Bridge — cloning the project, configuring API keys, running `go run`, and generating Codex config files. Switching between OpenAI and DeepSeek meant manually swapping `config.toml`, managing Moon Bridge's terminal process, and toggling VPN. CodexSwitch automates the entire workflow into one click.


## Features

- **One-click config switching**: switch between OpenAI and DeepSeek with one click
- **Moon Bridge auto-management**: compile, start, health check, stop - all automatic
- **Path discovery**: first-time setup guides you to select the Moon Bridge directory
- **Smart switching**: detects Codex running state, warns before killing, prompts manual start
- **System tray**: left-click show window, right-click quick actions
- **Boot autostart**: via Windows Registry, toggle in GUI
- **No Python required**: single portable exe (PyInstaller bundle)

## Usage

### Configuration file

On first run, the tool auto-creates config at:

```
C:\Users\<your-username>\.codex-switcher\config.yaml
```

No manual editing needed. All settings are managed through the GUI.

### First run

1. Double-click CodexSwitch.exe or run python main.py
2. Click "Switch to DeepSeek"
3. If Moon Bridge path is not set, a folder dialog will open
4. Select your moon-bridge project directory
5. The tool compiles moonbridge.exe, starts it, switches config

### Quick reference

| Action | Behavior |
|--------|----------|
| Switch to OpenAI | Switch config, prompt manual Codex start |
| Switch to DeepSeek | Start MB, switch config, prompt manual Codex start |
| Stop Moon Bridge | Kill moonbridge.exe |
| Window close (x) | Hide to system tray |
| Quit button | Dialog: Exit or Minimize to Tray |
| Tray left-click | Show window |
| Tray right-click | Quick switch / Exit |

### VPN note

VPN ON -> Start Codex (OpenAI needs VPN)
  -> Switch to DeepSeek: turn VPN OFF for stability
  -> Stay on OpenAI: keep VPN ON

## Build from source

Requires Python 3.10+:

```powershell
cd F:\VibeCoding\CodexSwitch
pip install -r requirements.txt
pip install pyinstaller
pyinstaller CodexSwitch.spec
```

## Tech stack

| Component | Purpose |
|-----------|---------|
| Python 3.12 | Runtime |
| customtkinter | Desktop GUI |
| pystray | System tray |
| PyYAML | Config persistence |
| Pillow | Tray icon |
| PyInstaller | Single exe build |
| Go | Moon Bridge compilation |

## License

MIT
