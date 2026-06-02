"""AutoStartCodex — Codex Config Switcher entry point.

Usage:
    python main.py          # Open GUI window
    python main.py --tray   # Start minimized to system tray
"""

from __future__ import annotations

import sys
import threading

from core.config_manager import ConfigManager
from core.config_switcher import ConfigSwitcher
from core.moon_bridge import MoonBridgeManager
from core.codex_launcher import CodexLauncher


def main():
    config_mgr = ConfigManager()
    config_mgr.load()

    switcher = ConfigSwitcher(config_mgr)
    moonbridge = MoonBridgeManager()
    codex = CodexLauncher()

    mb_dir = config_mgr.get_moonbridge_dir()
    if mb_dir:
        moonbridge.set_path(str(mb_dir))

    start_minimized = "--tray" in sys.argv

    if config_mgr.config.auto_start and not start_minimized:
        _auto_start(config_mgr, switcher, moonbridge, codex)

    _start_gui(config_mgr, switcher, moonbridge, codex, start_minimized)


def _auto_start(
    config_mgr: ConfigManager,
    switcher: ConfigSwitcher,
    moonbridge: MoonBridgeManager,
    codex: CodexLauncher,
) -> None:
    target = config_mgr.config.default_profile
    success, msg = switcher.switch_to(target)
    if not success:
        print(f"[autostart] Config switch failed: {msg}")
        return

    if target.needs_moonbridge:
        mb_dir = config_mgr.get_moonbridge_dir()
        if mb_dir:
            moonbridge.set_path(str(mb_dir))
            if not moonbridge.is_running():
                success, msg = moonbridge.start()
                if not success:
                    print(f"[autostart] Moon Bridge start failed: {msg}")
                    return

    success, msg = codex.launch()
    print(f"[autostart] {msg}")




def _on_full_quit(app):
    """Fully quit the application, stopping Moon Bridge first."""
    app.quit()
    app.destroy()


def _start_gui(
    config_mgr: ConfigManager,
    switcher: ConfigSwitcher,
    moonbridge: MoonBridgeManager,
    codex: CodexLauncher,
    start_minimized: bool,
) -> None:
    from app.ui import MainWindow

    app = MainWindow(config_mgr, switcher, moonbridge, codex, quit_callback=lambda: _on_full_quit(app))

    if start_minimized:
        app.withdraw()

    # Always start system tray (for window close → tray, quick switches)
    _start_tray_async(config_mgr, moonbridge, app)

    app.mainloop()


def _start_tray_async(config_mgr, moonbridge, app):
    from app.tray import TrayManager

    tray = TrayManager(
        on_switch_openai=lambda: _tray_switch("openai", config_mgr, moonbridge, app),
        on_switch_deepseek=lambda: _tray_switch("deepseek", config_mgr, moonbridge, app),
        on_show_window=lambda: app.after(0, app.deiconify),
        on_quit=app._handle_quit,
    )

    def run_tray():
        tray.start()

    t = threading.Thread(target=run_tray, daemon=True)
    t.start()


def _tray_switch(profile_name, config_mgr, moonbridge, app):
    from core.models import ProfileType
    from core.config_switcher import ConfigSwitcher
    from core.codex_launcher import CodexLauncher

    target = ProfileType(profile_name)
    switcher = ConfigSwitcher(config_mgr)
    codex = CodexLauncher()

    if target.needs_moonbridge:
        mb_dir = config_mgr.get_moonbridge_dir()
        if mb_dir:
            moonbridge.set_path(str(mb_dir))
            if not moonbridge.is_running():
                moonbridge.start()

    switcher.switch_to(target)
    codex.restart()
    app.after(0, lambda: getattr(app, "_refresh_state", lambda: None)())


if __name__ == "__main__":
    main()

