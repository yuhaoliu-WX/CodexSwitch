"""Codex App lifecycle: find, launch, restart on Windows."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Optional

CODEX_SEARCH_PATHS = [
    None,
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Codex",
    Path(os.environ.get("LOCALAPPDATA", "")) / "OpenAI" / "Codex",
    Path.home() / "AppData" / "Local" / "OpenAI" / "Codex",
]


class CodexLauncher:
    """Find and manage the Codex desktop application."""

    def __init__(self):
        self._codex_path: Optional[Path] = None

    def find_codex(self) -> Optional[Path]:
        """Locate the Codex executable."""
        if self._codex_path and self._codex_path.is_file():
            return self._codex_path

        codex_exe = self._which("codex")
        if codex_exe:
            self._codex_path = Path(codex_exe)
            return self._codex_path

        for base in CODEX_SEARCH_PATHS:
            if base is None:
                continue
            if not base.is_dir():
                continue
            for exe in sorted(base.rglob("codex.exe")):
                if exe.is_file():
                    self._codex_path = exe
                    return exe

        return None

    def launch(self) -> tuple[bool, str]:
        """
        Launch the Codex desktop app.

        Priority 1: `codex` shell command (App Execution Alias).
        This works for Windows App Store installs (WindowsApps is protected).
        Does NOT rely on exit code — exit code 1 can mean "already running".

        Priority 2: direct binary path fallback.
        Returns (success, message). On failure the caller should prompt the user.
        """
        # Priority 1: shell command
        try:
            before = self.is_running()
            proc = subprocess.Popen(
                ["codex"],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            # Wait briefly then check if the process appeared
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass
            # After launch attempt, check process table
            time.sleep(1)
            if self.is_running() or not before:
                return True, "Codex started"
            # Process didn't appear — could be that the command launched it
            # but exited. Give it one more second.
            time.sleep(2)
            if self.is_running():
                return True, "Codex started"
            return False, "Codex launch failed — exit code check skipped"
        except FileNotFoundError:
            pass

        # Priority 2: direct binary path
        exe = self.find_codex()
        if exe:
            try:
                before = self.is_running()
                subprocess.Popen(
                    [str(exe)],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                time.sleep(2)
                if self.is_running() or not before:
                    return True, f"Codex started ({exe.name})"
                return False, "Codex binary launch failed"
            except (FileNotFoundError, PermissionError, OSError):
                pass

        return False, "Codex not found. Please make sure Codex is installed."

    def is_running(self) -> bool:
        """Check if Codex process is running."""
        try:
            result = subprocess.run(
                ["tasklist", "/NH", "/FI", "IMAGENAME eq codex.exe"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "codex.exe" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def kill(self) -> bool:
        """Kill all Codex processes."""
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "codex.exe"],
                capture_output=True,
                timeout=5,
            )
            time.sleep(0.5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def restart(self) -> tuple[bool, str]:
        """Restart Codex: kill then launch."""
        was_running = self.is_running()
        if was_running:
            self.kill()
            time.sleep(1)
        return self.launch()

    @staticmethod
    def _which(name: str) -> Optional[str]:
        """Simple `which` equivalent."""
        try:
            result = subprocess.run(
                ["where", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
