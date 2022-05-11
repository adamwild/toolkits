import re

# definition of the language expression
# changes compared to the official one:
# - punctuation is not processed
# - word definition is more strict (not allow "~@#{")

# white space           = ? Unicode General Category Zs and CHARACTER TABULATION (U+0009) ? ;
WHITE_SPACE = r"[ \t]+"
# metadata = ">", ">", { text item - ":" }-, ":", { text item }-, new line character ;
METADATA = r"(?:(?<=\n)|^)>>([^:\n]+):([^\n]+)\n"
# text item = ? any character except new line character ? ;
TEXT_ITEM = r"[^\n]"
# word      = { text item - white space - punctuation character }- ;
WORD = r"[^~@#{ \t\n\r\.,;]+"
# units    = { text item - "}" }- ;
UNITS = r"[^\n}]*"
# quantity = { text item - "%" - "}" }- ;
QUANTITY = r"[^\n}%]*"
# amount   = quantity | ( quantity, "%", units ) ;
AMOUNT = rf"({QUANTITY})(?:%({UNITS}))?"
# one word ingredient  = "@", ( word,                     [ "{", [ amount ], "}" ] ) ;
ONE_WORD_ITEM = rf"({WORD})(?:{{{AMOUNT}}})?"
ONE_WORD_INGREDIENT = rf"@{ONE_WORD_ITEM}"
# multiword ingredient = "@", ( word, { text item - "{" }-, "{", [ amount ], "}" ) ;
MULTIWORD_ITEM = rf"({WORD}{WHITE_SPACE}[^\n{{~@#]*){{{AMOUNT}}}"
MULTIWORD_INGREDIENT = rf"@{MULTIWORD_ITEM}"
# one word cookware    = "#", ( word,                     [ "{", [ quantity ], "}" ] ) ;
ONE_WORD_COOKWARE = rf"#{ONE_WORD_ITEM}"
# multiword cookware   = "#", ( word, { text item - "{" }-, "{", [ quantity ], "}" ) ;
MULTIWORD_COOKWARE = rf"#{MULTIWORD_ITEM}"
# no name timer        = "~", (                             "{", [ amount ], "}" ) ;
NO_NAME_TIMER = rf"~{{{AMOUNT}}}"
# one word timer       = "~", ( word,                     [ "{", [ amount ], "}" ] ) ;
ONE_WORD_TIMER = rf"~{ONE_WORD_ITEM}"
# multiword timer      = "~", ( word, { text item - "{" }-, "{", [ amount ], "}" ) ;
MULTIWORD_TIMER = rf"~{MULTIWORD_ITEM}"
# new line character    = ? newline characters (U+000A ~ U+000D, U+0085, U+2028, and U+2029) ? ;
NEW_LINE = r"[\n\r]+"
# comments       = "-", "-", text item, new line character ;
INLINE_COMMENT = rf"--({TEXT_ITEM}*)(?=\n)"
# block comments = "[", "-", ? any character except "-" followed by "]" ?, "-", "]" ;
BLOCK_COMMENT = r"\[-((?:[^-]|-[^\]])*)-\]"


def p_handler(quantity: str, default_value: str = "") -> str:
    """function called by the lexer to process quantity and units strings

    if the quantity is not defined, then replace it by `default_value`.
    If it can be parsed as float, then parse it
    """
    quantity = quantity or ""  # handle None case
    quantity = quantity.strip()
    if not quantity:
        return default_value
    return quantity


# lexer definition. Rules will be executed in this order
pre_lexer_rules = [
    BLOCK_COMMENT,
    INLINE_COMMENT,
]

lexer_rules = [
    (METADATA, lambda x: {"type": "metadata", "key": x[0].strip(), "value": x[1].strip()}),
    (
        MULTIWORD_INGREDIENT,
        lambda x: {"type": "ingredient", "name": x[0], "quantity": p_handler(x[1], "some"), "units": p_handler(x[2])},
    ),
    (
        ONE_WORD_INGREDIENT,
        lambda x: {"type": "ingredient", "name": x[0], "quantity": p_handler(x[1], "some"), "units": p_handler(x[2])},
    ),
    (MULTIWORD_COOKWARE, lambda x: {"type": "cookware", "name": x[0], "quantity": p_handler(x[1], "1")}),
    (ONE_WORD_COOKWARE, lambda x: {"type": "cookware", "name": x[0], "quantity": p_handler(x[1], "1")}),
    (
        NO_NAME_TIMER,
        lambda x: {"type": "timer", "name": "", "quantity": p_handler(x[0], "1"), "units": p_handler(x[1])},
    ),
    (
        MULTIWORD_TIMER,
        lambda x: {"type": "timer", "name": x[0], "quantity": p_handler(x[1], "1"), "units": p_handler(x[2])},
    ),
    (
        ONE_WORD_TIMER,
        lambda x: {"type": "timer", "name": x[0], "quantity": p_handler(x[1], "1"), "units": p_handler(x[2])},
    ),
    (NEW_LINE, lambda x: {"type": "newline"}),
    (r"(.+)", lambda x: {"type": "text", "value": x[0]}),
]


def load(filename: str) -> list[dict]:
    with open(filename) as f:
        return parse("".join(f.readlines()))


def parse_quantity(quantity: str) -> str:
    """parse the quantity to have the official behavior (convert to float)"""
    if re.search(r"[a-z]", quantity, re.IGNORECASE):
        return quantity
    if "/" in quantity:
        frac_part = quantity.split("/")
        if len(frac_part) == 2:
            try:
                return float(frac_part[0]) / float(frac_part[1])
            except ValueError:
                return quantity
    try:
        return float(quantity)
    except ValueError:
        return quantity


def parse(text: str) -> list[dict]:
    """Parse the text using the official cooklang spec.
    This function passes the canonical tests defined in cooklang main repo
    """
    tokens = run_lexer(text)
    steps = [[]]
    metadata = {}
    for t in tokens:
        if t["type"] == "metadata":
            metadata[t["key"]] = t["value"]
        elif t["type"] == "newline":
            if steps[-1] != []:
                steps.append([])
        elif t["type"] == "text":
            steps[-1].append(t)
        else:
            t["quantity"] = parse_quantity(t["quantity"])
            steps[-1].append(t)
    if not steps[-1]:
        steps = steps[:-1]
    return {"metadata": metadata, "steps": steps}


def run_lexer(text: str) -> list[dict]:
    """run the pre-processing (comment removal) and the lexer"""
    # apply pre-processing of the text
    for rule in pre_lexer_rules:
        text = re.sub(rule, "", text)

    # apply lexer rules
    return _apply_lexer(text, lexer_rules)


def _apply_lexer(text: str, lexer_rules: list[tuple]) -> list[dict]:
    """apply the first rule of the list of lexer rules, then
    call itself on the non-parsed part of the text
    """
    rule = lexer_rules[0]
    last_text_id = 0
    r = []
    for m in re.finditer(rule[0], text):
        if m.start() != last_text_id:
            r += _apply_lexer(text[last_text_id : m.start()], lexer_rules[1:])
        r.append(rule[1](m.groups()))
        last_text_id = m.end()
    if last_text_id != len(text) and lexer_rules[1:]:
        r += _apply_lexer(text[last_text_id:], lexer_rules[1:])
    return r
