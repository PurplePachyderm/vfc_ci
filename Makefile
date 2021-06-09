CC = verificarlo-c
VFC_LIB_PATH=/usr/local/lib

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
	clang -c -fPIC vfc_hashmap.c vfc_probes.c

	clang vfc_hashmap.o -shared -o libvfc_hashmap.so
	clang vfc_probes.o -shared -o libvfc_probes.so
	cp *.so $(VFC_LIB_PATH)

	flang -c vfc_probes.f90
	flang -c vfc_probes_test.f90
	flang vfc_probes_test.o libvfc_hashmap.so libvfc_probes.so -o fortran_test


clean:
	rm -f test fortran_test
	rm -f *.o *.mod
