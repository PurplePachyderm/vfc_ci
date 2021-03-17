## vfc_ci

**[WIP]** Verificarlo CI is a test repository for the development of
automatically generated [Verificarlo](https://github.com/verificarlo/verificarlo)
test reports.

This is the `master` (or "dev") branch : everytime changes are pushed to this
branch, Verificarlo test results will be pushed to the Verificarlo CI branch
(`vfc_ci_master`) by the test workflow (executed on this branch). A new
HTML report will also be generated.

### Setup

Run the `vfc_ci_setup.sh` script. If you are on the `dev` branch, this will
create a test workflow on it (`.github/workflows/vfc_test_workflow.yml`),
as well as a `dev_vfc_ci` branch.
