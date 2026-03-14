"""Parser scaffold for QR payload interpretation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedPayload:
    raw: str
    fields: list[str]


def parse_payload(payload: str) -> ParsedPayload:
    """Return raw payload and provisional field split scaffold.

    Current behaviour intentionally keeps output template based on the full raw payload.
    """

    return ParsedPayload(raw=payload, fields=payload.split("?"))
