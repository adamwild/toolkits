%option noyywrap

%{
#include <stdlib.h>
#include "y.tab.h"
void yyerror(char *);
%}

NEW_LINE            [\n\r]
WHITE_SPACE         [ \t]+

NOT_COOKLANG_CHAR   [^\[\-~@#{}% \t\n\r]

BEGIN_COMMENT       "--"
BEGIN_BLOCK_COMMENT "[-"
END_BLOCK_COMMENT   "-]"
BEGIN_METADATA      ">>"

ZERO                "0"
NON_ZERO_DIGIT      [1-9]
DIGIT               ({ZERO}|{NON_ZERO_DIGIT})
INTEGER             ({ZERO}|({NON_ZERO_DIGIT}{DIGIT}*))
DECIMAL             {INTEGER}"."{INTEGER}
FRACTIONAL          {INTEGER}{WHITE_SPACE}*"/"{WHITE_SPACE}*{INTEGER}
NUMBER              {DIGIT}|{INTEGER}|{DECIMAL}|{FRACTIONAL}

/*
a word can be composed of:
  * not cooklang char
  * "[" not followed by "-" (else comment)
  * "-" not followed by a second "-" (else comment)
*/
WORD                ({NOT_COOKLANG_CHAR}|("["+[^-])|("-"[^-]))+
MULTIWORD           {WORD}{WHITE_SPACE}({WORD}|{WHITE_SPACE})*{WORD}

/*
  a block comment starty by [-, finish by -] and cannot contain -] inside
*/
BLOCK_COMMENT        {BEGIN_BLOCK_COMMENT}([^-]|"-"+[^\]])*{END_BLOCK_COMMENT}

/*
  metadata starts by >>, then contains at least one char different than ":", then a ":", then at least one char
*/
METADATA            {BEGIN_METADATA}[^:]+":".+


%%


{BLOCK_COMMENT}         {}
{BEGIN_COMMENT}.*       {}
{METADATA}              {yylval.string = strdup(yytext); return METADATA;}

{NEW_LINE}              return NL;
{WHITE_SPACE}           return WS;
"~"                     return TILDE;
"@"                     return AT;
"#"                     return H;
":"                     return DOUBLE_DOTS;
"{"                     return LCURL;
"}"                     return RCURL;
"%"                     return PERCENT;

{NUMBER}                { yylval.number = strtod(yytext, NULL); return NUMBER;}
{MULTIWORD}             { yylval.string = strdup(yytext);
                          return MULTIWORD;
                        }
{WORD}                  { yylval.string = strdup(yytext);
                          return WORD;
                        }

.                       printf("something else:%s\n", yytext);

%%


int main( int argc,char ** argv ){
    printf("plop\n");
    ++argv, --argc;  /* skip over program name */
    if ( argc > 0 ){
            printf("positive argc\n");
            yyin = fopen( argv[0], "r" );
    }
    else
            yyin = stdin;

    printf("start parser\n");
    yyparse();


    return 0;
}
