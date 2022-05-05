# flex

https://www.lrde.epita.fr/~tiger/doc/flex-2.5.22.html


# example 1: very basic stuff

```sh
mkdir out
flex -o out/example1.c example1.l
gcc out/example1.c -o out/example1
./out/example1 test.txt
```

# example 2: negative conditions


```sh
mkdir out
flex -o out/example2.c example2.l
gcc out/example2.c -o out/example2
./out/example2 test2.txt
```


# example 3: a full cooklang spec
see
https://github.com/cooklang/cooklang-c/blob/main/src/Cooklang.l
https://github.com/cooklang/spec/blob/main/EBNF.md

```sh
mkdir out
flex -o out/example3.c example3.l
gcc out/example3.c -o out/example3
./out/example3 test3.txt
```
