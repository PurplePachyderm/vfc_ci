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

vfc_probes:
	clang -c vfc_hashmap.c vfc_probes.c
	flang -c vfc_probes.f90
	flang vfc_probes_test.f90 vfc_hashmap.o vfc_probes.o -o fortran_test

clean:
	rm -f test fortran_test
	rm -f *.o *.mod
