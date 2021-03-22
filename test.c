// This is a test that will be compiled with Verificarlo

#include <stdio.h>
#include "vfc_probe.h"

int main(void) {

    ProbesHT probes;
    init_probes_ht(&probes);

    double res = 0;

    for(int i=0; i<100; i++) {
        res = res + 0.01;
        res = res - 0.01;

        put_probe(&probes, "test", VAR_NAME(res), res);
    }

    float varf = 42.0f;


    put_probe(&probes, "test", VAR_NAME(varf), varf);

    dump_probes_ht(&probes, "test.csv");
    free_probes_ht(&probes);

    // Old way of getting C test results
    printf("%lf\n", res);
}
