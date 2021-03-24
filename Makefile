CC = verificarlo-c

tests:
	$(CC) test.c -o test

hashmap:
	gcc -c vfc_hashmap.c

clean:
	rm test
