CC = verificarlo-c

tests:
	$(CC) test.c -o test

autopep:
	autopep8 --in-place --aggressive --aggressive vfc_ci
	autopep8 --in-place --aggressive --aggressive --recursive ci

install:
	git submodule init
	git submodule update

	bash copy_source.sh


clean:
	rm test
