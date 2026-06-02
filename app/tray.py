"""System tray icon with quick actions."""

from __future__ import annotations

from typing import Optional, Callable

from PIL import Image, ImageDraw

from core.models import ProfileType, MoonBridgeStatus

# ── Generate a simple tray icon ─────────────────────────────────
ICON_SIZE = 64


def _generate_icon() -> Image.Image:
    """Generate a simple colored icon for the system tray."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([2, 2, ICON_SIZE - 2, ICON_SIZE - 2], fill="#2B2B3D", outline="#4FC3F7", width=3)

    cx, cy = ICON_SIZE // 2, ICON_SIZE // 2
    r_inner = 14
    draw.ellipse(
        [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
        outline="#4FC3F7", width=3,
    )

    draw.polygon(
        [(cx + 4, cy - 8), (cx + 4, cy + 8), (cx + 16, cy)],
        fill="#4FC3F7",
    )

    return img


ICON_IMAGE = _generate_icon()


class TrayManager:
    """Manage system tray icon with pystray."""

    def __init__(
        self,
        on_switch_openai: Callable[[], None],
        on_switch_deepseek: Callable[[], None],
        on_show_window: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        self._icon: Optional["pystray.Icon"] = None
        self._on_switch_openai = on_switch_openai
        self._on_switch_deepseek = on_switch_deepseek
        self._on_show_window = on_show_window
        self._on_quit = on_quit
        self._current_profile: ProfileType = ProfileType.OPENAI
        self._mb_status: MoonBridgeStatus = MoonBridgeStatus.UNKNOWN

    def update_state(self, profile: ProfileType, mb_status: MoonBridgeStatus) -> None:
        """Update menu to reflect current state."""
        self._current_profile = profile
        self._mb_status = mb_status
        if self._icon:
            self._icon.menu = self._build_menu()
            self._icon.title = f"Codex Switcher - {profile.display_name}"

    def _build_menu(self):
        """Build the right-click menu."""
        import pystray

        status_text = f"Current: {self._current_profile.display_name}"
        mb_text = (
            f"Moon Bridge: {self._mb_status.value}"
            if self._current_profile.needs_moonbridge
            else "Moon Bridge: N/A"
        )

        return pystray.Menu(
            # Default item (left-click) → show window
            pystray.MenuItem(
                "Show Window",
                lambda: self._on_show_window(),
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(status_text, None, enabled=False),
            pystray.MenuItem(mb_text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Switch to OpenAI",
                lambda: self._on_switch_openai(),
                checked=lambda _item: self._current_profile == ProfileType.OPENAI,
            ),
            pystray.MenuItem(
                "Switch to DeepSeek",
                lambda: self._on_switch_deepseek(),
                checked=lambda _item: self._current_profile == ProfileType.DEEPSEEK,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show Window", lambda: self._on_show_window()),
            pystray.MenuItem("Exit", lambda: self._on_quit()),
        )

    def start(self) -> None:
        """Start the tray icon (blocking — run in a thread)."""
        import pystray

        self._icon = pystray.Icon(
            "codex-switcher",
            ICON_IMAGE,
            "Codex Config Switcher",
            menu=self._build_menu(),
        )
        self._icon.run()

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon:
            self._icon.stop()
            self._icon = None