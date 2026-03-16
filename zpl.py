"""ZPL rendering from template placeholders."""

from __future__ import annotations

from pathlib import Path

from parser import ParsedPayload


class TemplateError(RuntimeError):
    """Raised when required placeholders are missing."""


def _escape_zpl_field_data(value: str) -> str:
    return value.replace("^", "^^").replace("~", "~~")


def render_zpl(template_path: Path, parsed_payload: ParsedPayload) -> str:
    template = template_path.read_text(encoding="utf-8")

    if "{{QR_PAYLOAD}}" not in template:
        raise TemplateError("Template must include {{QR_PAYLOAD}} placeholder")

    replacements = {
        "{{TEXT_PAYLOAD}}": _escape_zpl_field_data(parsed_payload.text_payload),
        "{{TOP_LINE}}": _escape_zpl_field_data(parsed_payload.labornummer or parsed_payload.raw),
        "{{PRODUCT_NAME}}": _escape_zpl_field_data(parsed_payload.matrix),
        "{{DATE_LINE}}": _escape_zpl_field_data(f"T:{parsed_payload.date}" if parsed_payload.date else ""),
        "{{QR_PAYLOAD}}": _escape_zpl_field_data(parsed_payload.raw),
    }

    rendered = template
    for marker, replacement in replacements.items():
        rendered = rendered.replace(marker, replacement)

    return rendered
