%option noyywrap

%{
int num_lines = 0, num_chars = 0;
%}

NEW_LINE            [\n\r]
WHITE_SPACE         [ \t]+

COOKLANG_CHAR       [->~@#:{}% \t\n\r]
NOT_COOKLANG_CHAR   [^\[\-~@#:{}% \t\n\r>]

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
  * ">" not followed by a second ">" (else metadata)
*/
WORD                ({NOT_COOKLANG_CHAR}|("["+[^-])|("-"[^-])|(">"[^>]))+
MULTIWORD           {WORD}{WHITE_SPACE}({WORD}|{WHITE_SPACE})*{WORD}

%%
{BEGIN_BLOCK_COMMENT}([^\-]|"-"+[^\]])*{END_BLOCK_COMMENT}  printf("a block comment:%s\n", yytext);
{BEGIN_COMMENT}[^\n\r]*                                    printf("a comment:%s\n", yytext);

{BEGIN_METADATA}        printf("a metadata:%s\n", yytext);
{NUMBER}                printf("a number:%s\n", yytext);
{MULTIWORD}             printf("a multiword:%s\n", yytext);
{WORD}                  printf("a word:%s\n", yytext);

{NEW_LINE}              printf("a NL\n");
{WHITE_SPACE}           printf("a space\n");
"~"                     printf("a ~\n");
"@"                     printf("a @\n");
"#"                     printf("a #\n");
":"                     printf("a :\n");
"{"                     printf("a {\n");
"}"                     printf("a }\n");
"%"                     printf("a %\n");

{COOKLANG_CHAR}         printf("a cooklang char:%s\n", yytext);
{NOT_COOKLANG_CHAR}     printf("not a cooklang char:%s\n", yytext);
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

    yylex();
    printf( "# of lines = %d, # of chars = %d\n",
                         num_lines, num_chars );

    return 0;
}
