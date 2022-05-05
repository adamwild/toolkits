%option noyywrap

%{
int num_lines = 0, num_chars = 0;
%}

NEW_LINE            [\n\r]
WHITE_SPACE         [ \t]+
COOKLANG_CHAR       [->~@#:{}% \t\n\r]
NOT_COOKLANG_CHAR   [^->~@#:{}% \t\n\r]


%%


{COOKLANG_CHAR} printf("a cooklang char:%s\n", yytext);
{NOT_COOKLANG_CHAR} printf("not a cooklang char:%s\n", yytext);
.       printf("something else:%s\n", yytext);

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
