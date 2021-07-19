// This is a test that will be compiled with Verificarlo

#include <stdio.h>
#include <vfc_probes.h>

int main(void) {

  vfc_probes probes = vfc_init_probes();
  double res = 11;
  float varf = 42.4242f;

  for (int i = 0; i < 10; i++) {
    res = res + 1.0;

    varf = varf + 0.01;
    varf = varf - 0.01;
  }

  vfc_probe(&probes, "test", VAR_NAME(res), res);
  vfc_probe_check(&probes, "test", VAR_NAME(varf), varf, 1e-15);
  vfc_dump_probes(&probes);

  return 0;
}
