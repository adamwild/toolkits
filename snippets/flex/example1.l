%option noyywrap

%{
int num_lines = 0, num_chars = 0;
%}



%%
\n      ++num_lines; ++num_chars;
.       ++num_chars;

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
