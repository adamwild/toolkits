import unittest

import cooklang


class TestNumber(unittest.TestCase):
    def test_basic(self) -> None:
        test_cases = [
            {
                "input": "@thyme{20000%springs}\n",
                "output_ingredient_q": 20000.000,
            },
            {
                "input": "@thyme{2 000%springs}\n",
                "output_ingredient_q": "2 000",
            },
            {
                "input": "@thyme{20 000%springs}\n",
                "output_ingredient_q": "20 000",
            },
        ]

        for test_case in test_cases:
            output = cooklang.parse(test_case["input"])
            print(output)
            self.assertEqual(output["steps"][0][0]["quantity"], test_case["output_ingredient_q"])
