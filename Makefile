CC = gcc

tests:
	$(CC) test.c -o test

clean:
	rm test
