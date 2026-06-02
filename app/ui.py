"""Main GUI window using customtkinter."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import customtkinter as ctk

from core.models import ProfileType, AppStatus
from tkinter import messagebox
from core.config_manager import ConfigManager
from core.config_switcher import ConfigSwitcher
from core.moon_bridge import MoonBridgeManager
from core.codex_launcher import CodexLauncher
from app.theme import LIGHT, FONT_TITLE, FONT_BODY, FONT_SMALL, FONT_BUTTON, FONT_MONO

THEME = LIGHT  # Current theme dict, swap to DARK later if needed


class MainWindow(ctk.CTk):
    def __init__(
        self,
        config_mgr: ConfigManager,
        switcher: ConfigSwitcher,
        moonbridge: MoonBridgeManager,
        codex: CodexLauncher,
        quit_callback: callable,
    ):
        super().__init__()
        self.config_mgr = config_mgr
        self.switcher = switcher
        self.moonbridge = moonbridge
        self.codex = codex
        self._quit_callback = quit_callback
        self._app_status = AppStatus.IDLE
        self._current_profile = self.switcher.get_current_profile()
        self._switch_aborted = False
        self._hc_running = True  # health check thread flag

        self.title("Codex Config Switcher")
        self.geometry("720x440")
        self.minsize(640, 400)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 720) // 2
        y = (sh - 440) // 2
        self.geometry(f"720x440+{x}+{y}")

        # Close → withdraw to tray (not quit)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self.moonbridge.on_status_change(lambda s: self.after(0, self._refresh_state))
        self.after(100, self._refresh_state)

        # Start background health check thread
        self._start_hc_thread()

    # ── UI Construction ────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=0)  # buttons
        self.grid_rowconfigure(2, weight=0)  # status
        self.grid_rowconfigure(3, weight=1)  # log
        self.grid_rowconfigure(4, weight=0)  # footer

        T = THEME

        # ── Row 0: Header ──
        ctk.CTkLabel(
            self, text="Codex Config Switcher", font=FONT_TITLE,
            text_color=T["text"], anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))

        # ── Row 1: Action buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 8))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self._btn_openai = ctk.CTkButton(
            btn_frame, text="Switch to OpenAI", font=FONT_BUTTON,
            fg_color=T["openai_bg"], hover_color="#D0E8E3",
            text_color=T["openai"], border_color=T["openai"],
            border_width=2, corner_radius=10, height=56,
            command=lambda: self._do_switch(ProfileType.OPENAI),
        )
        self._btn_openai.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self._btn_deepseek = ctk.CTkButton(
            btn_frame, text="Switch to DeepSeek", font=FONT_BUTTON,
            fg_color=T["deepseek_bg"], hover_color="#D6EAF8",
            text_color=T["deepseek"], border_color=T["deepseek"],
            border_width=2, corner_radius=10, height=56,
            command=lambda: self._do_switch(ProfileType.DEEPSEEK),
        )
        self._btn_deepseek.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # ── Row 2: Status bar ──
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
        status_frame.grid_columnconfigure(0, weight=0)
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_columnconfigure(2, weight=0)

        self._status_label = ctk.CTkLabel(
            status_frame, text="", font=FONT_BODY, text_color=T["text"],
        )
        self._status_label.grid(row=0, column=0, sticky="w")

        self._status_detail = ctk.CTkLabel(
            status_frame, text="", font=FONT_SMALL, text_color=T["text_secondary"],
        )
        self._status_detail.grid(row=0, column=1, sticky="w", padx=(12, 0))

        self._progress = ctk.CTkProgressBar(status_frame, mode="indeterminate", width=120)
        self._progress.grid(row=0, column=2, sticky="e")
        self._progress.grid_remove()

        # ── Row 3: Log ──
        log_frame = ctk.CTkFrame(self, fg_color=T["surface"], corner_radius=10)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 8))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame, text="Log", font=("Segoe UI", 11, "bold"),
            text_color=T["text_secondary"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(8, 2))

        self._log_textbox = ctk.CTkTextbox(
            log_frame, font=FONT_MONO, fg_color=T["log_bg"],
            text_color=T["log_text"], corner_radius=6, border_width=0,
        )
        self._log_textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 10))
        self._log_textbox.configure(state="disabled")

        # ── Row 4: Footer ──
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 12))
        footer.grid_columnconfigure(0, weight=0)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=0)
        footer.grid_columnconfigure(3, weight=0)

        # Autostart
        self._autostart_var = ctk.BooleanVar(value=self.config_mgr.is_autostart_enabled())
        self._autostart_cb = ctk.CTkCheckBox(
            footer, text="Start on boot", variable=self._autostart_var,
            command=self._on_autostart_toggle, font=FONT_SMALL,
            text_color=T["text"], checkbox_width=18, checkbox_height=18,
        )
        self._autostart_cb.grid(row=0, column=0, sticky="w", padx=(0, 12))

        # Moon Bridge path button
        self._path_btn = ctk.CTkButton(
            footer, text="Set Moon Bridge path", font=FONT_SMALL,
            width=150, height=28, corner_radius=6,
            fg_color=T["surface"], text_color=T["text"],
            hover_color="#E8E8E8", border_width=1, border_color="#DDD",
            command=self._browse_moonbridge,
        )
        self._path_btn.grid(row=0, column=1, sticky="w")

        # Stop MB button
        self._stop_mb_btn = ctk.CTkButton(
            footer, text="Stop Moon Bridge", font=FONT_SMALL,
            width=120, height=28, corner_radius=6,
            fg_color="#FDF2F2", text_color="#C0392B",
            hover_color="#FADBD8", border_width=1, border_color="#E6B0AA",
            command=self._stop_moonbridge,
        )
        self._stop_mb_btn.grid(row=0, column=2, padx=(8, 0))

        # Quit button
        self._quit_btn = ctk.CTkButton(
            footer, text="Quit", font=("Segoe UI", 12, "bold"),
            width=70, height=28, corner_radius=6,
            fg_color="transparent", text_color=T["text_secondary"],
            hover_color="#E8E8E8", border_width=0,
            command=self._show_quit_dialog,
        )
        self._quit_btn.grid(row=0, column=3, padx=(8, 0))

    # ── Switch logic ───────────────────────────────────────

    def _do_switch(self, target: ProfileType):
        if self._app_status == AppStatus.SWITCHING:
            self._log("Switch already in progress")
            return

        # Check if we need to kill Codex (only when switching profiles)
        already_on_target = self._current_profile == target
        if already_on_target:
            # Only managing Moon Bridge, no Codex restart needed
            self._begin_switch_thread(target, kill_codex=False)
            return

        codex_running = self.codex.is_running()
        if codex_running:
            # Need user confirmation before killing Codex
            self._ask_kill_codex(target)
        else:
            # Codex not running, just switch config and prompt
            self._begin_switch_thread(target, kill_codex=False)

    def _switch_sync(self, target: ProfileType, kill_codex: bool):
        # Step 1: Handle Moon Bridge
        if target.needs_moonbridge:
            self.after(0, lambda: self._set_status_text(
                f"Preparing {target.display_name} ...", THEME["yellow"]))
            mb_path = self.config_mgr.get_moonbridge_dir()
            if not mb_path:
                self._log("Moon Bridge path not configured")
                self._switch_aborted = True
                self.after(0, self._abort_and_prompt_moonbridge)
                return
            self.moonbridge.set_path(str(mb_path))
            if not self.moonbridge.is_running():
                self._log("Starting Moon Bridge ...")
                success, msg = self.moonbridge.start(
                    progress_callback=lambda s: self.after(0, lambda: self._log(s)))
                if not success:
                    self._log(f"Moon Bridge start failed: {msg}")
                    return
                self._log("Moon Bridge started")
            else:
                self._log("Moon Bridge already running")
        else:
            if self.moonbridge.is_running():
                self._log("Moon Bridge still running (can close with Stop button)")

        # Step 2: Kill Codex if needed
        if kill_codex:
            self._log("Closing Codex ...")
            self.codex.kill()
            time.sleep(1)
            self._log("Codex closed")

        # Step 3: Switch config
        self.after(0, lambda: self._set_status_text(
            f"Switching to {target.display_name} ...", THEME["yellow"]))
        success, msg = self.switcher.switch_to(target)
        if not success:
            self._log(f"Config switch failed: {msg}")
            return
        self._log(msg)

        # Step 4: Prompt user to start Codex manually
        self._log("Configuration switched. Please start Codex manually.")
        self.after(0, lambda: self._show_manual_start_dialog())
        self._current_profile = target

    def _ask_kill_codex(self, target: ProfileType):
        """Show a confirmation dialog before killing Codex."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Close Codex?")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"380x180+{x}+{y}")

        ctk.CTkLabel(
            dialog, text="Codex is currently running.",
            font=("Segoe UI", 14, "bold"), text_color=THEME["text"],
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            dialog, text="It will be closed to apply the new configuration.\nPlease save your work before continuing.",
            font=("Segoe UI", 12), text_color=THEME["text_secondary"],
            justify="center",
        ).pack(pady=(0, 14))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        def on_confirm():
            dialog.destroy()
            self._begin_switch_thread(target, kill_codex=True)

        def on_cancel():
            dialog.destroy()
            self._app_status = AppStatus.IDLE
            self._refresh_state()

        ctk.CTkButton(
            btn_frame, text="Close Codex and Switch", font=("Segoe UI", 12, "bold"),
            width=150, height=34, corner_radius=8,
            fg_color="#E74C3C", hover_color="#C0392B",
            text_color="white", command=on_confirm,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Cancel", font=("Segoe UI", 12),
            width=100, height=34, corner_radius=8,
            fg_color=THEME["surface"], text_color=THEME["text"],
            hover_color="#E8E8E8", border_width=1, border_color="#DDD",
            command=on_cancel,
        ).pack(side="left")

    def _begin_switch_thread(self, target: ProfileType, kill_codex: bool):
        """Start the background switch thread."""
        self._app_status = AppStatus.SWITCHING
        self._switch_aborted = False
        self._set_buttons_enabled(False)
        self._progress.grid()
        self._progress.start()
        self._log(f"Switching to {target.display_name} ...")

        def task():
            try:
                self._switch_sync(target, kill_codex)
            finally:
                if not self._switch_aborted:
                    self.after(0, self._on_switch_done)

        threading.Thread(target=task, daemon=True).start()

    def _show_manual_start_dialog(self):
        """Inform the user to start Codex manually."""
        messagebox.showinfo(
            "Start Codex Manually",
            "The Codex configuration has been switched.\n\n"
            "Please start Codex manually to use the new configuration."
        )

    def _on_switch_done(self):
        self._app_status = AppStatus.IDLE
        self._progress.stop()
        self._progress.grid_remove()
        self._set_buttons_enabled(True)
        self._refresh_state()

    def _abort_and_prompt_moonbridge(self):
        self._app_status = AppStatus.IDLE
        self._progress.stop()
        self._progress.grid_remove()
        self._set_buttons_enabled(True)
        self._set_status_text("Please configure Moon Bridge path", THEME["red"])
        self._log("Moon Bridge path required to switch to DeepSeek")
        self._browse_moonbridge()

    def _browse_moonbridge(self):
        from tkinter import filedialog, messagebox
        initial = self.config_mgr.config.moonbridge_path or str(Path.home())
        d = filedialog.askdirectory(title="Select Moon Bridge project", initialdir=initial)
        if not d:
            return
        valid, msg = self.moonbridge.validate_path(d)
        if not valid:
            self._log(f"Invalid: {msg}")
            messagebox.showerror("Invalid path", msg)
            self.after(100, self._browse_moonbridge)
            return
        self.config_mgr.set_moonbridge_path(d)
        self.moonbridge.set_path(d)
        self._log(f"Moon Bridge path set: {d}")

    def _stop_moonbridge(self):
        self._log("Stopping Moon Bridge ...")
        self.moonbridge.stop()
        self._log("Moon Bridge stopped")
        self._refresh_state()

    # ── Health check thread (background, non-blocking) ─────

    def _start_hc_thread(self):
        def loop():
            while self._hc_running:
                try:
                    self.moonbridge.health_check()
                    self.after(0, self._refresh_state)
                except Exception:
                    pass
                time.sleep(10)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    # ── State updates ──────────────────────────────────────

    def _refresh_state(self):
        profile = self.switcher.get_current_profile()
        self._current_profile = profile
        mb_dir = self.config_mgr.get_moonbridge_dir()
        T = THEME

        if profile == ProfileType.DEEPSEEK and mb_dir and self.moonbridge.is_running():
            self._set_status_text(f"Current: {profile.display_name}", T["green"])
            self._status_detail.configure(text="Moon Bridge: running")
            self._stop_mb_btn.configure(state="normal")
        elif profile == ProfileType.DEEPSEEK and mb_dir:
            self._set_status_text(f"Current: {profile.display_name}", T["red"])
            self._status_detail.configure(text="Moon Bridge: stopped")
            self._stop_mb_btn.configure(state="disabled")
        elif profile == ProfileType.OPENAI:
            self._set_status_text(f"Current: {profile.display_name}", T["green"])
            self._status_detail.configure(text="Moon Bridge: not needed")
            self._stop_mb_btn.configure(state="disabled" if not self.moonbridge.is_running() else "normal")
        else:
            self._set_status_text("Status unknown", T["text"])
            self._status_detail.configure(text="")
            self._stop_mb_btn.configure(state="disabled")

    def _set_status_text(self, text: str, color: str = ""):
        self._status_label.configure(text=text, text_color=color or THEME["text"])

    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._btn_openai.configure(state=state)
        self._btn_deepseek.configure(state=state)

    def _log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def append():
            self._log_textbox.configure(state="normal")
            self._log_textbox.insert("end", line)
            self._log_textbox.see("end")
            self._log_textbox.configure(state="disabled")
        self.after(0, append)

    # ── Events ─────────────────────────────────────────────

    def _on_autostart_toggle(self):
        self.config_mgr.set_auto_start(self._autostart_var.get())

    def _on_close(self):
        # Window × button: hide to tray, keep Moon Bridge running
        self.withdraw()

    def _show_quit_dialog(self):
        """Show a dialog asking Exit or Minimize to Tray."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Codex Config Switcher")
        dialog.geometry("340x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        x = self.winfo_x() + (self.winfo_width() - 340) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"340x180+{x}+{y}")

        ctk.CTkLabel(
            dialog, text="What would you like to do?",
            font=("Segoe UI", 14, "bold"), text_color=THEME["text"],
        ).pack(pady=(24, 8))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(8, 0))

        def do_exit():
            dialog.destroy()
            self._handle_quit()

        def do_minimize():
            dialog.destroy()
            self.withdraw()

        ctk.CTkButton(
            btn_frame, text="Exit", font=("Segoe UI", 13, "bold"),
            width=100, height=38, corner_radius=8,
            fg_color="#E74C3C", hover_color="#C0392B",
            text_color="white", command=do_exit,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Minimize to Tray", font=("Segoe UI", 13),
            width=140, height=38, corner_radius=8,
            fg_color=THEME["surface"], text_color=THEME["text"],
            hover_color="#E8E8E8", border_width=1, border_color="#DDD",
            command=do_minimize,
        ).pack(side="left")

    def _handle_quit(self):
        """Full quit: stop Moon Bridge + exit."""
        self._hc_running = False
        if self.moonbridge.is_running():
            self._log("Stopping Moon Bridge ...")
            self.moonbridge.stop()
        if self._quit_callback:
            self._quit_callback()