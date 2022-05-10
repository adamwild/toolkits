import re
import unittest

from cooklang.parser import BLOCK_COMMENT, INLINE_COMMENT, MULTIWORD_INGREDIENT, ONE_WORD_INGREDIENT, WORD


class TestRegexes(unittest.TestCase):
    def apply_regex_on_texts(self, texts_and_comments: list[tuple[str, list]], regex: str) -> None:
        for t, c in texts_and_comments:
            self.assertEqual(re.findall(regex, t), c, t)

    def test_block_comment(self) -> None:
        texts_and_comments = [
            ("hello world [-comment-]", ["comment"]),
            ("hello\nworld [-multiline\ncomment-]\n", ["multiline\ncomment"]),
            ("hello [- [ -]", [" [ "]),
            ("hello [- -] -]", [" "]),
            ("hello [- [- -]", [" [- "]),
            ("hello [- h -] world [-w-]", [" h ", "w"]),
        ]
        self.apply_regex_on_texts(texts_and_comments, BLOCK_COMMENT)

    def test_inline_comment(self) -> None:
        texts_and_comments = [
            ("test--comment\n", ["comment"]),
            ("test-comment\n", []),
            ("test--comment\ntest2--comment2\n", ["comment", "comment2"]),
            ("test--comment--plop\n", ["comment--plop"]),
        ]
        self.apply_regex_on_texts(texts_and_comments, INLINE_COMMENT)

    def test_word(self) -> None:
        texts_and_comments = [
            ("test--comment\n", ["test--comment"]),
            ("test--comment\ntest2--comment2\n", ["test--comment", "test2--comment2"]),
            ("test--comment--plop\n", ["test--comment--plop"]),
        ]
        self.apply_regex_on_texts(texts_and_comments, f"({WORD})")

    def test_one_word_ingredient(self) -> None:
        texts_and_comments = [
            ("@ingredient", [("ingredient", "", "")]),
            ("@ingredient{}", [("ingredient", "", "")]),
            ("@ingredient{1}", [("ingredient", "1", "")]),
            ("@ingredient{1%g}", [("ingredient", "1", "g")]),
            ("@ingre-dient{1%g}", [("ingre-dient", "1", "g")]),
        ]

        self.apply_regex_on_texts(texts_and_comments, ONE_WORD_INGREDIENT)

    def test_multiword_ingredient(self) -> None:
        texts_and_comments = [
            ("@ingre dient", []),
            ("@ingre dient{}", [("ingre dient", "", "")]),
            ("@ingre dient {1}", [("ingre dient ", "1", "")]),
            ("@ingre dient  {1%g}", [("ingre dient  ", "1", "g")]),
            ("@ingre-d ient{1%g}", [("ingre-d ient", "1", "g")]),
        ]
        self.apply_regex_on_texts(texts_and_comments, MULTIWORD_INGREDIENT)
