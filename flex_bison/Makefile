OBJ=bin/CooklangParser.o bin/CooklangRecipe.o bin/LinkedListLib.o


clean:
	rm -r out

build:
	mkdir -p out
	bison example1.y -d -v -o out/y.tab.c
	flex -o out/example1.c example1.l
	gcc out/example1.c out/y.tab.c -o out/example1
