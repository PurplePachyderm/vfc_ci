CC = clang-7
FC=flang
VFC = verificarlo-c
VFC_LIB_PATH=/usr/local/lib

tests:
	$(CC) test.c -lvfc_probes -o test

autopep:
	autopep8 --in-place --aggressive --aggressive vfc_ci
	autopep8 --in-place --aggressive --aggressive --recursive ci

install:
	git submodule init
	git submodule update

	$(CC) -c -fPIC vfc_hashmap.c vfc_probes.c
	$(CC) vfc_probes.o vfc_hashmap.o -shared -o libvfc_probes.so

	bash copy_source.sh
	ldconfig

vfc_probes:
	$(CC) -c -fPIC vfc_hashmap.c vfc_probes.c

	$(CC) vfc_probes.o vfc_hashmap.o -shared -o libvfc_probes.so
	cp *.so $(VFC_LIB_PATH)
	ldconfig

	$(FC) -c vfc_probes_f.f90
	$(FC) -c vfc_probes_test.f90
	$(FC) vfc_probes_test.o libvfc_probes.so -o fortran_test


clean:
	rm -f test fortran_test
	rm -f *.o *.so *.mod
