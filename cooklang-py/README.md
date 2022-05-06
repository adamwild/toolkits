# Cooklang

Cooklang parser implementation following closely the EBNF of the language:
https://github.com/cooklang/spec/blob/main/EBNF.md

EBNF description:
```EBNF
recipe = { metadata | step }- ;

(* not sure how to show that, but two below should start from a new line *)
metadata = ">", ">", { text item - ":" }-, ":", { text item }-, new line character ;
step     = { text item | ingredient | cookware | timer }-, new line character ;

ingredient           = one word ingredient | multiword ingredient ;
one word ingredient  = "@", ( word,                     [ "{", [ amount ], "}" ] ) ;
multiword ingredient = "@", ( word, { text item - "{" }-, "{", [ amount ], "}" ) ;

cookware             = one word cookware | multiword cookware ;
one word cookware    = "#", ( word,                     [ "{", [ quantity ], "}" ] ) ;
multiword cookware   = "#", ( word, { text item - "{" }-, "{", [ quantity ], "}" ) ;

timer                = no name timer | one word timer | multiword timer ;
no name timer        = "~", (                             "{", [ amount ], "}" ) ;
one word timer       = "~", ( word,                     [ "{", [ amount ], "}" ] ) ;
multiword timer      = "~", ( word, { text item - "{" }-, "{", [ amount ], "}" ) ;

amount   = quantity | ( quantity, "%", units ) ;
quantity = { text item - "%" - "}" }- ;
units    = { text item - "}" }- ;

word      = { text item - white space - punctuation character }- ;
text item = ? any character except new line character ? ;

(* https://en.wikipedia.org/wiki/Template:General_Category_(Unicode) *)
new line character    = ? newline characters (U+000A ~ U+000D, U+0085, U+2028, and U+2029) ? ;
white space           = ? Unicode General Category Zs and CHARACTER TABULATION (U+0009) ? ;
punctuation character = ? Unicode General Category P* ? ;

comments       = "-", "-", text item, new line character ;
block comments = "[", "-", ? any character except "-" followed by "]" ?, "-", "]" ;
```

a parser is usually made of 2 parts: a lexer and a grammar. Here, the language is so that
we don't need to implement a grammar. The lexer part is enough.

The canonical tests are based on the yaml files of the spec repo and the c++ repo.


## Installation

## Usage

## TODO
- [ ] first version
- [ ] test
