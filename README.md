## vfc_ci

**[WIP]** Verificarlo CI is a test repository for the development of
automatically generated [Verificarlo](https://github.com/verificarlo/verificarlo)
test reports.

This is the `master` (or "dev") branch : everytime changes are pushed to this
branch, Verificarlo test results will be pushed to the Verificarlo CI branch
(`vfc_ci_master`) by the "test" workflow (executed on this branch).

Then, the "report" workflow on the CI branch will generate/update an HTML
report that can be visualized anytime.
