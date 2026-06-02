"""Data models and enumerations for CodexSwitch."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProfileType(str, Enum):
    """Available Codex configuration profiles."""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"

    @property
    def display_name(self) -> str:
        names = {
            ProfileType.OPENAI: "OpenAI",
            ProfileType.DEEPSEEK: "DeepSeek",
        }
        return names[self]

    @property
    def config_filename(self) -> str:
        filenames = {
            ProfileType.OPENAI: "config-openai.toml",
            ProfileType.DEEPSEEK: "config-deepseek.toml",
        }
        return filenames[self]

    @property
    def needs_moonbridge(self) -> bool:
        return self == ProfileType.DEEPSEEK


class MoonBridgeStatus(str, Enum):
    """Current status of the Moon Bridge process."""

    UNKNOWN = "unknown"
    NOT_FOUND = "not_found"
    PATH_INVALID = "path_invalid"
    COMPILING = "compiling"
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class CodexStatus(str, Enum):
    """Current status of the Codex application."""

    UNKNOWN = "unknown"
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"


class AppStatus(str, Enum):
    """Overall tool status."""

    IDLE = "idle"
    SWITCHING = "switching"
    ERROR = "error"


@dataclass
class Profile:
    """Represents a configurable Codex profile."""

    name: str
    config_filename: str
    needs_moonbridge: bool
    description: str = ""


@dataclass
class ToolConfig:
    """Persistent tool configuration stored in config.yaml."""

    # Version tracking
    config_version: int = 1

    # Default behavior
    default_profile: ProfileType = ProfileType.OPENAI
    auto_start: bool = False
    start_minimized: bool = False

    # Last used profile (for restoring state)
    last_profile: Optional[ProfileType] = None

    # Moon Bridge settings
    moonbridge_path: str = ""
    moonbridge_exe_path: str = ""
    moonbridge_auto_compile: bool = True

    # Profiles (extensible)
    profiles: dict = field(default_factory=lambda: {
        "openai": {
            "name": "OpenAI",
            "config_file": "config-openai.toml",
            "needs_moonbridge": False,
        },
        "deepseek": {
            "name": "DeepSeek",
            "config_file": "config-deepseek.toml",
            "needs_moonbridge": True,
        },
    })

