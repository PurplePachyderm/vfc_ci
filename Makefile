CC = clang
FC= flang
VFC = verificarlo-c
VFC_LIB_PATH=/usr/local/lib

tests:
	$(VFC) test.c -lvfc_probes -o test

format:
	autopep8 --in-place --aggressive --aggressive vfc_ci
	autopep8 --in-place --aggressive --aggressive --recursive ci
	clang-format -i vfc_probes.h vfc_probes.c

install:
	git submodule init
	git submodule update

	$(CC) -c -fPIC vfc_hashmap.c vfc_probes.c
	$(CC) vfc_probes.o vfc_hashmap.o -shared -o libvfc_probes.so
	ar rcvf libvfc_probes.a vfc_probes.o vfc_hashmap.o

	$(FC) -c vfc_probes_f.f90
	ar rcvf libvfc_probes_f.a vfc_probes_f.o

	bash copy_source.sh
	ldconfig

vfc_probes:
	$(FC) -c vfc_probes_test.f90
	$(FC) vfc_probes_test.o -lvfc_probes -lvfc_probes_f -o fortran_test


clean:
	rm -f test fortran_test
	rm -f *.o *.so *.mod *.a
