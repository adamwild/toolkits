import unittest

from cooklang import parse


class TestParser(unittest.TestCase):
    def test_parser(self) -> None:
        r = parse("Add a bit of chilli")
        self.assertEqual(
            r,
            {
                "metadata": {},
                "steps": [[{"type": "text", "value": "Add a bit of chilli"}]],
            },
        )
        r = parse("@thyme{2%springs} -- testing comments\nand some text\n")

    def test_mix_ingredients(self) -> None:
        r = parse("le @basilic et les @olives{Environ 20}")
        self.assertEqual(
            r,
            {
                "metadata": {},
                "steps": [
                    [
                        {"type": "text", "value": "le "},
                        {"type": "ingredient", "name": "basilic", "quantity": "some", "units": ""},
                        {"type": "text", "value": " et les "},
                        {"type": "ingredient", "name": "olives", "quantity": "Environ 20", "units": ""},
                    ]
                ],
            },
        )
