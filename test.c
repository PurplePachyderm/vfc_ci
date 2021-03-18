// This is a test that will be compiled with Verificarlo

#include <stdio.h>

int main(void) {
    double res = 0;

    for(int i=0; i<10000; i++) {
        res = res + 0.01;
    }

    res -= 100;

    printf("%lf", res);
}
