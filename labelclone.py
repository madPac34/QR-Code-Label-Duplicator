#!/usr/bin/env python3
"""Headless QR-to-label duplicator service."""

from __future__ import annotations

import importlib.util
import logging
import time
from pathlib import Path

from evdev import InputDevice, categorize, ecodes

from keyboard_layouts import UnsupportedLayoutError, get_layout
from parser import parse_payload
from zpl import TemplateError, render_zpl

LOGGER = logging.getLogger("labelclone")


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config():
    config_path = Path(__file__).with_name("config.py")
    if config_path.exists():
        return _load_module_from_path("runtime_config", config_path)

    example_path = Path(__file__).with_name("config.example.py")
    if example_path.exists():
        LOGGER.warning("config.py not found, falling back to config.example.py")
        return _load_module_from_path("default_config", example_path)

    raise FileNotFoundError("Neither config.py nor config.example.py could be loaded")

def detect_scanner_device(configured_device: str | None) -> str:
    if configured_device:
        return configured_device

    by_id_dir = Path("/dev/input/by-id")
    candidates = sorted(by_id_dir.glob("*event-kbd"))
    if not candidates:
        raise FileNotFoundError(
            "No scanner device found in /dev/input/by-id/*event-kbd. "
            "Set SCANNER_DEVICE in config.py."
        )

    return str(candidates[0].resolve())


def iter_scanned_payloads(device_path: str, layout_name: str):
    layout = get_layout(layout_name)
    scanner = InputDevice(device_path)
    LOGGER.info("Listening to scanner device: %s", scanner.path)

    buffer: list[str] = []
    shift_pressed = False

    for event in scanner.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        key_event = categorize(event)
        keycode = key_event.scancode

        if keycode in (ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT):
            shift_pressed = key_event.keystate != key_event.key_up
            continue

        if key_event.keystate != key_event.key_down:
            continue

        if keycode == ecodes.KEY_ENTER:
            payload = "".join(buffer).strip()
            buffer.clear()
            if payload:
                yield payload
            continue

        if keycode == ecodes.KEY_BACKSPACE:
            if buffer:
                buffer.pop()
            continue

        if keycode not in layout:
            LOGGER.debug("Ignoring unmapped keycode: %s", keycode)
            continue

        normal, shifted = layout[keycode]
        buffer.append(shifted if shift_pressed else normal)


def print_label(printer_device: str, zpl_text: str) -> None:
    with open(printer_device, "wb") as printer:
        printer.write(zpl_text.encode("utf-8"))


def save_latest_zpl(output_directory: Path, zpl_text: str) -> Path:
    output_directory.mkdir(parents=True, exist_ok=True)
    latest_path = output_directory / "latest.zpl"
    latest_path.write_text(zpl_text, encoding="utf-8")
    return latest_path


def configure_logging(enable_log_file: bool, log_file_path: Path) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if enable_log_file:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file_path, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )


def run() -> None:
    config = load_config()
    enable_test_log_file = bool(getattr(config, "ENABLE_TEST_LOG_FILE", False))
    test_log_file_path = Path(
        getattr(config, "TEST_LOG_FILE_PATH", Path("/tmp/labelclone-testing/labelclone.log"))
    )
    enable_test_zpl_fallback = bool(getattr(config, "ENABLE_TEST_ZPL_FALLBACK", False))
    test_zpl_output_directory = Path(
        getattr(config, "TEST_ZPL_OUTPUT_DIR", Path("/tmp/labelclone-testing"))
    )
    configure_logging(enable_test_log_file, test_log_file_path)

    scanner_device = detect_scanner_device(getattr(config, "SCANNER_DEVICE", None))
    keyboard_layout = getattr(config, "KEYBOARD_LAYOUT", "de")
    printer_device = getattr(config, "PRINTER_DEVICE", "/dev/usb/lp0")
    template_path = Path(getattr(config, "TEMPLATE_PATH", Path("templates/label_template.zpl")))
    dedupe_window = float(getattr(config, "DUPLICATE_SUPPRESSION_SECONDS", 0.5))

    last_payload = None
    last_print_ts = 0.0

    LOGGER.info("Using keyboard layout: %s", keyboard_layout)
    LOGGER.info("Using printer device: %s", printer_device)
    LOGGER.info("Using template: %s", template_path)
    if enable_test_log_file:
        LOGGER.info("Test log file enabled: %s", test_log_file_path)
    if enable_test_zpl_fallback:
        LOGGER.info("Test ZPL fallback enabled: %s/latest.zpl", test_zpl_output_directory)

    try:
        payload_stream = iter_scanned_payloads(scanner_device, keyboard_layout)

        for payload in payload_stream:
            now = time.monotonic()
            if payload == last_payload and now - last_print_ts < dedupe_window:
                LOGGER.info("Duplicate payload suppressed: %r", payload)
                continue

            parsed = parse_payload(payload)
            zpl_text = render_zpl(template_path, parsed)
            try:
                print_label(printer_device, zpl_text)
            except (FileNotFoundError, OSError) as exc:
                if not enable_test_zpl_fallback:
                    raise

                latest_path = save_latest_zpl(test_zpl_output_directory, zpl_text)
                LOGGER.warning(
                    "Printer unavailable (%s). Saved latest ZPL to %s",
                    exc,
                    latest_path,
                )

            last_payload = payload
            last_print_ts = now
            LOGGER.info("Printed payload: %r", payload)

    except (UnsupportedLayoutError, FileNotFoundError, PermissionError, TemplateError) as exc:
        LOGGER.exception("Fatal configuration/runtime error: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    run()
