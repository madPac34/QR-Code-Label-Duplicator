# QR-Code-Label-Duplicator

Headless Raspberry Pi service that listens to a USB QR scanner (keyboard/HID mode), rebuilds the scanned payload, and prints one duplicate sticky label to a raw ZPL printer.

## Features

- Reads scanner input directly from Linux event device (`/dev/input/event*`) using `evdev`.
- Auto-detects scanner from `/dev/input/by-id/*event-kbd`, with optional fixed-device override.
- Supports keyboard layout mapping for `de` and `us`.
- UTF-8 end-to-end (`^CI28` in ZPL + UTF-8 bytes to printer) including umlauts (`ä ö ü Ä Ö Ü ß`).
- Duplicate scan suppression (same payload scanned again within configured window is ignored).
- Template-based label rendering with placeholders for easy migration to a production layout.
- `systemd` unit for auto-start at boot and restart on failure.
- One-command installer script for Raspberry Pi OS Lite.

## Repository layout

- `labelclone.py` – main service loop and device I/O.
- `config.example.py` – configurable defaults (copy to `config.py`).
- `keyboard_layouts.py` – HID keycode to character mappings.
- `parser.py` – parser scaffold for future field-aware templates.
- `zpl.py` – template loading and placeholder rendering.
- `templates/label_template.zpl` – current test label template.
- `systemd/labelclone.service` – background service definition.
- `scripts/install.sh` – install/update helper for `/opt/labelclone`.

## Payload handling

Current test template prints:

1. Full raw payload as text.
2. QR code containing the exact same payload.

Example payload:

`FL26-030001?Tomato?20.03.26?`

The parser scaffold already splits on `?` and keeps the original raw payload, so you can later replace the template and mapping logic without changing scanner/printer plumbing.

## Installation (one command)

From cloned repo on Raspberry Pi OS Lite:

```bash
sudo ./scripts/install.sh
```

Installer actions:

1. Installs system packages (`python3`, `python3-venv`, `python3-pip`, `rsync`).
2. Syncs repo to `/opt/labelclone`.
3. Preserves existing `/opt/labelclone/config.py` on upgrades.
4. Creates virtual environment and installs Python dependencies.
5. Installs `systemd` service, enables it, and starts/restarts it.

## Configuration

After first install edit:

`/opt/labelclone/config.py`

Important keys:

- `SCANNER_DEVICE`: set explicit event device path or keep `None` for auto-detect.
- `KEYBOARD_LAYOUT`: `"de"` or `"us"`.
- `PRINTER_DEVICE`: raw printer path (default `/dev/usb/lp0`).
- `TEMPLATE_PATH`: path to ZPL template file.
- `DUPLICATE_SUPPRESSION_SECONDS`: duplicate-blocking window.

Then restart service:

```bash
sudo systemctl restart labelclone.service
```

## Service operations

```bash
sudo systemctl status labelclone.service
sudo journalctl -u labelclone.service -f
```

## Notes for production template migration

When payload format stabilizes, adapt:

- `parser.py` to map specific `?`-separated fields.
- `templates/label_template.zpl` placeholders/positions.
- optionally `zpl.py` to render additional placeholders.
