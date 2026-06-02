"""Tool configuration persistence: reads/writes config.yaml, manages auto-start registry."""

from __future__ import annotations

import os
import sys
import json
import shutil
import winreg
from pathlib import Path
from typing import Optional

import yaml

from core.models import ToolConfig, ProfileType

# Default config directory: ~/.codex-switcher/
CONFIG_DIR = Path.home() / ".codex-switcher"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
CODEX_HOME = Path.home() / ".codex"

AUTOSTART_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_NAME = "CodexConfigSwitcher"


def _resolve_tool_path() -> str:
    """Return the path to this tool's main.py for auto-start registry entry."""
    # If running from a PyInstaller bundle
    if getattr(sys, "frozen", False):
        return sys.executable
    # Running from source
    main_py = Path(sys.argv[0]).resolve()
    return f'"{sys.executable}" "{main_py}" --tray'


class ConfigManager:
    """Loads and saves the tool's own settings."""

    def __init__(self):
        self.config: ToolConfig = ToolConfig()

    # ── Load / Save ──────────────────────────────────────────────

    def load(self) -> ToolConfig:
        """Load config from disk, falling back to defaults."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if not CONFIG_FILE.exists():
            self.config = ToolConfig()
            self._save()
            return self.config

        try:
            raw = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
            if raw is None:
                self.config = ToolConfig()
                self._save()
                return self.config

            self.config = ToolConfig(
                config_version=raw.get("config_version", 1),
                default_profile=ProfileType(raw.get("default_profile", "openai")),
                auto_start=raw.get("auto_start", False),
                start_minimized=raw.get("start_minimized", False),
                last_profile=(
                    ProfileType(raw["last_profile"])
                    if raw.get("last_profile") else None
                ),
                moonbridge_path=raw.get("moonbridge_path", ""),
                moonbridge_exe_path=raw.get("moonbridge_exe_path", ""),
                moonbridge_auto_compile=raw.get("moonbridge_auto_compile", True),
                profiles=raw.get("profiles", self.config.profiles),
            )
        except Exception as exc:
            print(f"[config] Failed to load config.yaml, using defaults: {exc}")
            self.config = ToolConfig()

        return self.config

    def _save(self) -> None:
        """Write current config to disk."""
        data = {
            "config_version": self.config.config_version,
            "default_profile": self.config.default_profile.value,
            "auto_start": self.config.auto_start,
            "start_minimized": self.config.start_minimized,
            "last_profile": (
                self.config.last_profile.value if self.config.last_profile else None
            ),
            "moonbridge_path": self.config.moonbridge_path,
            "moonbridge_exe_path": self.config.moonbridge_exe_path,
            "moonbridge_auto_compile": self.config.moonbridge_auto_compile,
            "profiles": self.config.profiles,
        }
        CONFIG_FILE.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding="utf-8")

    def save(self) -> None:
        """Public save method."""
        self._save()

    # ── Quick property accessors ─────────────────────────────────

    def get_moonbridge_dir(self) -> Optional[Path]:
        """Return the validated moon-bridge directory, or None."""
        p = self.config.moonbridge_path.strip()
        if not p:
            return None
        path = Path(p)
        return path if path.is_dir() else None

    def set_moonbridge_path(self, path: str) -> None:
        self.config.moonbridge_path = path
        # Reset exe path — will be re-detected on next launch
        self.config.moonbridge_exe_path = ""
        self._save()

    def set_last_profile(self, profile: ProfileType) -> None:
        self.config.last_profile = profile
        self._save()

    def set_default_profile(self, profile: ProfileType) -> None:
        self.config.default_profile = profile
        self._save()

    def set_auto_start(self, enabled: bool) -> None:
        self.config.auto_start = enabled
        self._sync_autostart_registry()
        self._save()

    # ── Auto-start (Windows Registry) ────────────────────────────

    def _sync_autostart_registry(self) -> None:
        """Add or remove the auto-start registry entry."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, AUTOSTART_REG_KEY, 0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            ) as key:
                if self.config.auto_start:
                    winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, _resolve_tool_path())
                else:
                    try:
                        winreg.DeleteValue(key, AUTOSTART_NAME)
                    except OSError:
                        pass  # Value doesn't exist
        except PermissionError:
            print("[config] Permission denied writing auto-start registry")

    def is_autostart_enabled(self) -> bool:
        """Check if the registry entry exists (in case it was removed externally)."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, AUTOSTART_REG_KEY, 0, winreg.KEY_READ
            ) as key:
                winreg.QueryValueEx(key, AUTOSTART_NAME)
                return True
        except (OSError, FileNotFoundError):
            return False

    # ── Config file helpers ──────────────────────────────────────

    @staticmethod
    def codex_config_path() -> Path:
        return CODEX_HOME / "config.toml"

    @staticmethod
    def profile_config_path(profile: ProfileType) -> Path:
        return CODEX_HOME / profile.config_filename

    @staticmethod
    def detect_current_profile() -> Optional[ProfileType]:
        """Read current config.toml and determine which profile is active."""
        config_file = ConfigManager.codex_config_path()
        if not config_file.exists():
            return None
        try:
            text = config_file.read_text(encoding="utf-8")
            if "model_provider = \"moonbridge\"" in text:
                return ProfileType.DEEPSEEK
            return ProfileType.OPENAI
        except Exception:
            return None

