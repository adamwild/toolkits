import unittest

from cooklang import parse


class TestParser(unittest.TestCase):
    def test_parser(self):
        r = parse("Add a bit of chilli")
        self.assertEqual(
            r,
            {
                "metadata": {},
                "steps": [[{"type": "text", "value": "Add a bit of chilli"}]],
            },
        )
        r = parse("@thyme{2%springs} -- testing comments\nand some text\n")
        print(r)
