// This is a test that will be compiled with Verificarlo

#include <stdio.h>

int main(void) {
    double res = 0;

    for(int i=0; i<1000; i++) {
        res = res + 0.1;
    }

    printf("%lf\n", res);
}
