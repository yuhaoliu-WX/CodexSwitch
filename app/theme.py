"""Theme system for easy style switching."""

from __future__ import annotations

from typing import TypedDict


class ThemeDict(TypedDict):
    name: str
    bg: str
    surface: str
    text: str
    text_secondary: str
    openai: str
    openai_bg: str
    deepseek: str
    deepseek_bg: str
    green: str
    red: str
    yellow: str
    log_bg: str
    log_text: str
    entry_bg: str


# ── Dark theme ──
DARK: ThemeDict = {
    "name": "Dark",
    "bg": "#1E1E2E",
    "surface": "#2B2B3D",
    "text": "#E0E0E0",
    "text_secondary": "#9E9E9E",
    "openai": "#74AA9C",
    "openai_bg": "#1A2B26",
    "deepseek": "#4FC3F7",
    "deepseek_bg": "#0D1B2A",
    "green": "#2ECC71",
    "red": "#E74C3C",
    "yellow": "#F1C40F",
    "log_bg": "#1A1A2E",
    "log_text": "#B0B0C0",
    "entry_bg": "#1A1A2E",
}

# ── Light theme ──
LIGHT: ThemeDict = {
    "name": "Light",
    "bg": "#F5F5F5",
    "surface": "#FFFFFF",
    "text": "#333333",
    "text_secondary": "#888888",
    "openai": "#2E7D6F",
    "openai_bg": "#E0F2F1",
    "deepseek": "#1565C0",
    "deepseek_bg": "#E3F2FD",
    "green": "#27AE60",
    "red": "#E74C3C",
    "yellow": "#F39C12",
    "log_bg": "#FAFAFA",
    "log_text": "#555555",
    "entry_bg": "#FAFAFA",
}

THEMES = {"dark": DARK, "light": LIGHT}

FONT_TITLE = ("Segoe UI", 17, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 11)