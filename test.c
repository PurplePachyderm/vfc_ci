// This is a test that will be compiled with Verificarlo

#include <stdio.h>
#include "vfc_probe.h"

int main(void) {

    vfc_probes probes = vfc_init_probes();
    double res = 0;

    for(int i=0; i<10; i++) {
        res = res + 0.01;
        res = res - 0.01;
    }

    float varf = 42.4242f;

    vfc_put_probe(&probes, "test", VAR_NAME(res), res);
    vfc_put_probe(&probes, "test", VAR_NAME(varf), varf);

    vfc_dump_probes(&probes, "test.csv");
    vfc_free_probes(&probes);

    return 0;
}
