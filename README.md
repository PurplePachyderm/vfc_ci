## vfc_ci

[![Verificarlo CI (master)](https://github.com/PurplePachyderm/vfc_ci/actions/workflows/vfc_test_workflow.yml/badge.svg)](https://github.com/PurplePachyderm/vfc_ci/actions/workflows/vfc_test_workflow.yml)

This is a test repository for the development of Verificarlo CI, a
[Verificarlo](https://github.com/verificarlo/verificarlo)-based continuous
integration tool. Verificarlo CI lets you define, run, automatize, and visualize
custom Verificarlo tests.

This is the `master` (or "dev") branch : everytime changes are pushed to this
branch, Verificarlo test results will be pushed to the Verificarlo CI branch
(`vfc_ci_master`) by the test workflow (executed on this branch). These results
can be visualized by starting a server to serve an HTML report.

### Quick installation

The following installation procedure will install ```vfc_ci``` over an existing Verificarlo install.

- Create a `copy_source.sh` script. Here is an example file with hardcoded
values (most of the time, you will want to keep this exact file, maybe changing
the Python install path with your version) :

```
#!/usr/bin/env bash

VFC_INCLUDE_PATH=/usr/local/include
VFC_PYTHON_PATH=/usr/local/lib/python3.7/site-packages/verificarlo
VFC_BIN_PATH=/usr/local/bin
VFC_LIB_PATH=/usr/local/lib

cp vfc_hashmap.h $VFC_INCLUDE_PATH/vfc_hashmap.h
cp vfc_probes.h $VFC_INCLUDE_PATH/vfc_probes.h

cp vfc_ci $VFC_BIN_PATH
cp vfc_ci $VFC_PYTHON_PATH
cp -r ci $VFC_PYTHON_PATH
cp sigdigits/sigdigits.py $VFC_PYTHON_PATH

cp *.so $VFC_LIB_PATH
ldconfig
```

- Run you script directly, or `make install` (to also download sigdigits with Git submodules).


### Usage

The tool is used through a CLI interface, `vfc_ci`. There are 3 main subcommands :
- `vfc_ci setup`: create a Verificarlo CI workflow on your current branch
- `vfc_ci test`: execute your custom set of tests, and save their results
- `vfc_ci serve`: serve an HTML report to visualize all your test results

Run `vfc_ci --help` or `vfc_ci SUBCOMMAND --help` for more details.
