"""Keyboard mappings for scanner HID events."""

from __future__ import annotations

from evdev import ecodes


_LAYOUT_DE = {
    "KEY_SPACE": (" ", " "),
    "KEY_MINUS": ("ß", "?"),
    "KEY_EQUAL": ("´", "`"),
    "KEY_LEFTBRACE": ("ü", "Ü"),
    "KEY_RIGHTBRACE": ("+", "*"),
    "KEY_BACKSLASH": ("#", "'"),
    "KEY_SEMICOLON": ("ö", "Ö"),
    "KEY_APOSTROPHE": ("ä", "Ä"),
    "KEY_GRAVE": ("^", "°"),
    "KEY_COMMA": (",", ";"),
    "KEY_DOT": (".", ":"),
    "KEY_SLASH": ("-", "_"),
}

_LAYOUT_US = {
    "KEY_SPACE": (" ", " "),
    "KEY_MINUS": ("-", "_"),
    "KEY_EQUAL": ("=", "+"),
    "KEY_LEFTBRACE": ("[", "{"),
    "KEY_RIGHTBRACE": ("]", "}"),
    "KEY_BACKSLASH": ("\\", "|"),
    "KEY_SEMICOLON": (";", ":"),
    "KEY_APOSTROPHE": ("'", '"'),
    "KEY_GRAVE": ("`", "~"),
    "KEY_COMMA": (",", "<"),
    "KEY_DOT": (".", ">"),
    "KEY_SLASH": ("/", "?"),
}

_DIGIT_US_SHIFT = {
    "KEY_1": "!",
    "KEY_2": "@",
    "KEY_3": "#",
    "KEY_4": "$",
    "KEY_5": "%",
    "KEY_6": "^",
    "KEY_7": "&",
    "KEY_8": "*",
    "KEY_9": "(",
    "KEY_0": ")",
}

_DIGIT_DE_SHIFT = {
    "KEY_1": "!",
    "KEY_2": '"',
    "KEY_3": "§",
    "KEY_4": "$",
    "KEY_5": "%",
    "KEY_6": "&",
    "KEY_7": "/",
    "KEY_8": "(",
    "KEY_9": ")",
    "KEY_0": "=",
}


class UnsupportedLayoutError(ValueError):
    """Raised when an unknown keyboard layout is configured."""


def _base_layout() -> dict[str, tuple[str, str]]:
    mapping = {}

    for number in range(10):
        key = f"KEY_{number}"
        mapping[key] = (str(number), str(number))

    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        key = f"KEY_{char}"
        mapping[key] = (char.lower(), char)

    return mapping


def _build_layout(base: dict[str, tuple[str, str]], specific: dict[str, tuple[str, str]], shifted_digits: dict[str, str]) -> dict[int, tuple[str, str]]:
    layout = dict(base)
    layout.update(specific)

    for key_name, shifted in shifted_digits.items():
        normal, _ = layout[key_name]
        layout[key_name] = (normal, shifted)

    return {getattr(ecodes, name): pair for name, pair in layout.items() if hasattr(ecodes, name)}


def get_layout(layout_name: str) -> dict[int, tuple[str, str]]:
    base = _base_layout()

    if layout_name == "de":
        return _build_layout(base, _LAYOUT_DE, _DIGIT_DE_SHIFT)

    if layout_name == "us":
        return _build_layout(base, _LAYOUT_US, _DIGIT_US_SHIFT)

    raise UnsupportedLayoutError(f"Unsupported keyboard layout: {layout_name}")
