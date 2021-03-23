CC = verificarlo-c

tests:
	$(CC) test.c -o test

clean:
	rm test
