CC = verificarlo-c

tests:
	$(CC) test.c -o test

install:
	git submodule init
	git submodule update

	cp vfc_hashmap.h vfc_probes.h $(VFC_INCLUDE_PATH)
	cp vfc_ci $(VFC_PYTHON_PATH)
	cp -r ci $(VFC_PYTHON_PATH)
	cp sigdigits/sigdigits.py $(VFC_PYTHON_PATH)

	cp vfc_ci $(VFC_BIN_PATH)

clean:
	rm test
