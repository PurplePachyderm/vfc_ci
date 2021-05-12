CC = verificarlo-c

tests:
	$(CC) test.c -o test

install:
	git submodule init
	git submodule update

	bash copy_source.sh


clean:
	rm test
