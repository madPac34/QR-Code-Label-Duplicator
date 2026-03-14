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

    required = ("{{TEXT_PAYLOAD}}", "{{QR_PAYLOAD}}")
    if any(token not in template for token in required):
        raise TemplateError("Template must include {{TEXT_PAYLOAD}} and {{QR_PAYLOAD}} placeholders")

    replacements = {
        "{{TEXT_PAYLOAD}}": _escape_zpl_field_data(parsed_payload.raw),
        "{{QR_PAYLOAD}}": _escape_zpl_field_data(parsed_payload.raw),
    }

    rendered = template
    for marker, replacement in replacements.items():
        rendered = rendered.replace(marker, replacement)

    return rendered
