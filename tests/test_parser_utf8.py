import unittest

from parser import parse_payload


class ParsePayloadUtf8Tests(unittest.TestCase):
    def test_utf8_fields_are_preserved(self) -> None:
        payload = "LÄB-ß_Größe_2026-03-25"

        parsed = parse_payload(payload)

        self.assertEqual(parsed.raw, payload)
        self.assertEqual(parsed.labornummer, "LÄB-ß")
        self.assertEqual(parsed.matrix, "Größe")
        self.assertEqual(parsed.date, "2026-03-25")
        self.assertEqual(parsed.text_payload, "LÄB-ß\nGröße\nT:2026-03-25")

    def test_utf8_with_extra_underscores_keeps_matrix_mapping(self) -> None:
        payload = "ÄBC_Mäßig_kompliziert_2026-03-25"

        parsed = parse_payload(payload)

        self.assertEqual(parsed.labornummer, "ÄBC")
        self.assertEqual(parsed.matrix, "Mäßig_kompliziert")
        self.assertEqual(parsed.date, "2026-03-25")

    def test_non_structured_payload_with_utf8_falls_back_to_raw(self) -> None:
        payload = "Überraschung"

        parsed = parse_payload(payload)

        self.assertEqual(parsed.labornummer, "")
        self.assertEqual(parsed.matrix, "")
        self.assertEqual(parsed.date, "")
        self.assertEqual(parsed.text_payload, payload)


if __name__ == "__main__":
    unittest.main()
