"""Codex configuration file switching logic."""

from __future__ import annotations

import shutil
from pathlib import Path

from core.models import ProfileType
from core.config_manager import ConfigManager


class ConfigSwitcher:
    """Switch between Codex configuration profiles."""

    def __init__(self, config_mgr: ConfigManager):
        self._config_mgr = config_mgr

    def switch_to(self, profile: ProfileType) -> tuple[bool, str]:
        """
        Switch Codex to the given profile by copying the profile's
        config file over config.toml.

        Returns (success, message).
        """
        source = ConfigManager.profile_config_path(profile)
        target = ConfigManager.codex_config_path()

        if not source.exists():
            return (
                False,
                f"找不到配置文件: {source}\n"
                f"请先在 Codex 中配置好 {profile.display_name} 设置，"
                f"然后手动复制 config.toml 为 {profile.config_filename}",
            )

        # Backup current config
        if target.exists():
            backup = target.with_suffix(".toml.bak")
            try:
                shutil.copy2(target, backup)
            except OSError as exc:
                return False, f"备份当前配置失败: {exc}"

        # Copy the profile config
        try:
            shutil.copy2(source, target)
        except OSError as exc:
            return False, f"切换配置失败: {exc}"

        # Save last used profile
        self._config_mgr.set_last_profile(profile)

        return True, f"已切换到 {profile.display_name} 配置"

    @staticmethod
    def get_current_profile() -> ProfileType:
        """Detect which profile is currently active."""
        detected = ConfigManager.detect_current_profile()
        return detected if detected else ProfileType.OPENAI

    @staticmethod
    def validate_profile_config(profile: ProfileType) -> tuple[bool, str]:
        """Check if the profile's config file exists and looks valid."""
        path = ConfigManager.profile_config_path(profile)
        if not path.exists():
            return False, f"文件不存在: {path.name}"
        try:
            text = path.read_text(encoding="utf-8")
            if profile == ProfileType.DEEPSEEK and "moonbridge" not in text:
                return False, "DeepSeek 配置中未检测到 moonbridge 设置"
            if profile == ProfileType.OPENAI and "moonbridge" in text:
                return False, "OpenAI 配置中检测到 moonbridge 设置"
        except Exception as exc:
            return False, f"读取失败: {exc}"
        return True, "配置有效"

