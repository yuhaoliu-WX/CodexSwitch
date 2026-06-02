"""Moon Bridge lifecycle: path validation, compilation, start, stop, health check."""

from __future__ import annotations

import os
import threading
import subprocess
import socket
import time
import signal
from pathlib import Path
from typing import Optional, Callable

from core.models import MoonBridgeStatus

MOONBRIDGE_PORT = 38440
MOONBRIDGE_HOST = "127.0.0.1"
COMPILE_TIMEOUT_SEC = 120
START_TIMEOUT_SEC = 30
HEALTH_CHECK_INTERVAL = 0.3


class MoonBridgeManager:
    """Manage the Moon Bridge proxy process."""

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._dir_path: Optional[Path] = None
        self._exe_path: Optional[Path] = None
        self._status: MoonBridgeStatus = MoonBridgeStatus.UNKNOWN
        self._status_listeners: list[Callable[[MoonBridgeStatus], None]] = []
        self._log_buffer: list[str] = []
        # Health check cache (avoid blocking UI thread)
        self._last_hc_time: float = 0.0
        self._cached_hc_result: bool = False
        self._hc_cache_ttl: float = 2.0
        self._reader_thread: Optional[threading.Thread] = None

    # ── Path discovery & validation ──────────────────────────────

    def set_path(self, directory: str) -> None:
        """Set the moon-bridge directory path."""
        self._dir_path = Path(directory).resolve()
        self._exe_path = self._dir_path / "moonbridge.exe"
        self._status = MoonBridgeStatus.UNKNOWN

    def get_path(self) -> Optional[str]:
        return str(self._dir_path) if self._dir_path else None

    def validate_path(self, directory: str) -> tuple[bool, str]:
        """
        Validate that the given directory contains a moon-bridge project.
        Returns (is_valid, message).
        """
        path = Path(directory).resolve()
        if not path.is_dir():
            return False, f"目录不存在: {directory}"

        # Check for key files
        has_config = (path / "config.yml").is_file()
        has_cmd = (path / "cmd" / "moonbridge").is_dir()
        has_go_mod = (path / "go.mod").is_file()

        clues = []
        if has_config:
            clues.append("✓ config.yml")
        if has_cmd:
            clues.append("✓ cmd/moonbridge/")
        if has_go_mod:
            clues.append("✓ go.mod")

        if has_config and has_cmd and has_go_mod:
            return True, f"有效的 Moon Bridge 项目目录 ({', '.join(clues)})"

        if not clues:
            return False, "该目录不包含 Moon Bridge 项目文件"
        return False, f"目录不完整: 缺少必要文件 (仅有 {', '.join(clues)})"

    # ── Compilation ──────────────────────────────────────────────

    def needs_compilation(self) -> bool:
        """Check if the binary needs to be compiled (missing or outdated)."""
        if not self._dir_path or not self._dir_path.is_dir():
            return False
        if not self._exe_path or not self._exe_path.is_file():
            return True

        # Check if source files are newer than the binary
        exe_mtime = self._exe_path.stat().st_mtime
        for go_file in self._dir_path.rglob("*.go"):
            try:
                if go_file.stat().st_mtime > exe_mtime:
                    return True
            except OSError:
                continue
        return False

    def get_outdated_sources(self) -> list[str]:
        """Return list of .go files newer than the binary (for display)."""
        if not self._dir_path or not self._exe_path or not self._exe_path.is_file():
            return []
        exe_mtime = self._exe_path.stat().st_mtime
        changed = []
        for go_file in sorted(self._dir_path.rglob("*.go")):
            try:
                if go_file.stat().st_mtime > exe_mtime:
                    changed.append(str(go_file.relative_to(self._dir_path)))
            except OSError:
                continue
        return changed

    def compile(self, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Compile moonbridge.exe from source.
        Returns True on success.
        """
        if not self._dir_path:
            self._set_status(MoonBridgeStatus.PATH_INVALID)
            return False

        self._set_status(MoonBridgeStatus.COMPILING)
        self._log("开始编译 moonbridge.exe ...")

        if progress_callback:
            progress_callback("编译中...")

        try:
            result = subprocess.run(
                ["go", "build", "-o", "moonbridge.exe", "./cmd/moonbridge"],
                cwd=str(self._dir_path),
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT_SEC,
            )
        except subprocess.TimeoutExpired:
            self._log(f"编译超时 ({COMPILE_TIMEOUT_SEC}秒)")
            self._set_status(MoonBridgeStatus.ERROR)
            return False
        except FileNotFoundError:
            self._log("未找到 Go 编译器 (go 命令不可用)")
            self._set_status(MoonBridgeStatus.ERROR)
            return False

        if result.returncode != 0:
            self._log(f"编译失败:\n{result.stderr}")
            self._set_status(MoonBridgeStatus.ERROR)
            return False

        self._exe_path = self._dir_path / "moonbridge.exe"
        self._log("编译成功")
        return True

    # ── Lifecycle ────────────────────────────────────────────────

    def start(self, progress_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
        """
        Start Moon Bridge in a background process.
        Returns (success, message).
        """
        if not self._dir_path or not self._dir_path.is_dir():
            return False, "Moon Bridge 目录未配置"

        self._set_status(MoonBridgeStatus.STARTING)

        # Compile if needed
        if self.needs_compilation():
            changed = self.get_outdated_sources()
            if changed:
                hint = f"检测到 {len(changed)} 个源文件已更新"
                self._log(hint)
                if progress_callback:
                    progress_callback(hint)
            if not self.compile(progress_callback):
                return False, "Moon Bridge 编译失败"

        exe = self._exe_path or (self._dir_path / "moonbridge.exe")
        if not exe.is_file():
            return False, f"未找到 moonbridge.exe ({exe})"

        config_file = self._dir_path / "config.yml"
        if not config_file.is_file():
            return False, f"未找到 config.yml ({config_file})"

        self._log("启动 Moon Bridge ...")

        try:
            self._process = subprocess.Popen(
                [str(exe), "--config", str(config_file)],
                cwd=str(self._dir_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as exc:
            self._log(f"启动失败: {exc}")
            self._set_status(MoonBridgeStatus.ERROR)
            return False, f"启动失败: {exc}"

        # Wait for the server to be ready
        started = self._wait_for_ready(START_TIMEOUT_SEC, progress_callback)

        if started:
            self._set_status(MoonBridgeStatus.RUNNING)
            self._log("Moon Bridge 已就绪 (127.0.0.1:38440)")
            return True, "Moon Bridge 已启动"
        else:
            # Check if process died
            ret = self._process.poll()
            if ret is not None:
                self._log(f"进程已退出 (code={ret})")
                self._set_status(MoonBridgeStatus.ERROR)
                return False, f"Moon Bridge 进程已退出 (code={ret})"
            self._set_status(MoonBridgeStatus.RUNNING)
            return True, "Moon Bridge 可能已启动 (端口未确认)"

    def _reader_loop(self, stream) -> None:
        """Read Moon Bridge stdout in background and log lines."""
        try:
            while self._process and self._process.poll() is None:
                try:
                    raw = stream.readline()
                    if not raw:
                        break
                    line = raw.decode("utf-8", errors="replace").rstrip()
                    if line:
                        self._log(line)
                except Exception:
                    break
        except Exception:
            pass

    def stop(self) -> bool:
        """Stop Moon Bridge if running. Kills by process name for robustness."""
        self._log("Stopping Moon Bridge ...")
        # Kill tracked process if any
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    self._process.kill()
                    self._process.wait(timeout=2)
                except Exception:
                    pass
            except Exception:
                pass
            self._process = None
        # Also kill any moonbridge.exe by name (handles orphaned processes)
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "moonbridge.exe"],
                capture_output=True, timeout=5,
            )
        except Exception:
            pass
        # Clear cache so next check is fresh
        self._last_hc_time = 0.0
        self._cached_hc_result = False
        # Wait for port to close
        for _ in range(15):
            if not self._check_port():
                break
            time.sleep(0.3)
        self._set_status(MoonBridgeStatus.STOPPED)
        self._log("Moon Bridge stopped")
        return True

    def _wait_for_ready(
        self,
        timeout: float,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """Poll the TCP port until Moon Bridge responds.
        Does NOT read stdout (handled by a separate reader thread in start())."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._check_port():
                return True
            if self._process and self._process.poll() is not None:
                return False
            time.sleep(HEALTH_CHECK_INTERVAL)
        return self._check_port()

    # ── Health check ─────────────────────────────────────────────

    @staticmethod
    def _check_port() -> bool:
        """Check if something is listening on the Moon Bridge port."""
        try:
            with socket.create_connection(
                (MOONBRIDGE_HOST, MOONBRIDGE_PORT), timeout=0.3
            ):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def is_running(self) -> bool:
        """Check if Moon Bridge is running. Uses cached result when available."""
        if time.time() - self._last_hc_time < self._hc_cache_ttl:
            return self._cached_hc_result
        if self._process and self._process.poll() is None:
            port_open = self._check_port()
        else:
            port_open = self._check_port()
        self._last_hc_time = time.time()
        self._cached_hc_result = port_open
        if port_open:
            self._set_status(MoonBridgeStatus.RUNNING)
        return port_open

    def health_check(self) -> bool:
        """Quick health check with 2-second cache to avoid blocking the UI thread."""
        now = time.time()
        if now - self._last_hc_time < self._hc_cache_ttl:
            return self._cached_hc_result
        self._last_hc_time = now
        alive = self._check_port()
        self._cached_hc_result = alive
        if alive:
            if self._status != MoonBridgeStatus.RUNNING:
                self._set_status(MoonBridgeStatus.RUNNING)
        else:
            if self._status == MoonBridgeStatus.RUNNING:
                self._set_status(MoonBridgeStatus.STOPPED)
        return alive

    # ── Logging & status ─────────────────────────────────────────

    def _set_status(self, status: MoonBridgeStatus) -> None:
        self._status = status
        for cb in self._status_listeners:
            try:
                cb(status)
            except Exception:
                pass

    @property
    def status(self) -> MoonBridgeStatus:
        return self._status

    def get_recent_logs(self, n: int = 10) -> list[str]:
        return self._log_buffer[-n:]

    def _log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self._log_buffer.append(line)
        # Keep buffer bounded
        if len(self._log_buffer) > 500:
            self._log_buffer = self._log_buffer[-500:]

    def on_status_change(self, callback: Callable[[MoonBridgeStatus], None]) -> None:
        """Register a listener for status changes."""
        self._status_listeners.append(callback)

